import cv2
from ultralytics import YOLO
import argparse
import os
from pathlib import Path
import numpy as np
import time

def detect_pizzas_in_video(video_path, model_name='yolov8n.pt', confidence_threshold=0.5, classes_to_detect=None):
    # Down model
    try:
        model = YOLO(model_name)
    except Exception as e:
        print(f"Lỗi khi tải mô hình '{model_name}': {e}")
        print("Đảm bảo bạn có kết nối internet để tải mô hình lần đầu hoặc đường dẫn mô hình của bạn là chính xác.")
        return

    # Video
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Lỗi: Không thể mở tệp video tại {video_path}")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # frame_width = 1920
    # frame_height = 1080
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Video: {video_path}")
    print(f"Resolution: {frame_width}x{frame_height}, FPS: {fps}")
    
    # Resize window
    # cv2.namedWindow("Pizza Sales Counter", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Pizza Sales Counter", frame_width, frame_height)

    #### Use VideoWriter because using docker ####
    output_dir = Path("output_videos") # <-- Đường dẫn trong container
    output_dir.mkdir(parents=True, exist_ok=True)

    # output file
    video_filename_base = os.path.basename(video_path).split('.')[0]
    output_video_path = output_dir / f"{video_filename_base}_processed.mp4"

    # chóose Codec 
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # VideoWriter
    out = cv2.VideoWriter(str(output_video_path), fourcc, fps, (frame_width, frame_height))

    if not out.isOpened():
        print(f"Error: Could not create video writer for {output_video_path}")
        cap.release()
        return
    ####################

    # Class modify
    model_classes = model.names
    print(f"Classes to detect: {model_classes}")

    # Region count for each video
    counting_region = {
        "CH01.mp4": [[606, 88], [1378, 33], [1400, 176], [592, 253]],     #region video 1: [[606, 88], [1378, 33], [1400, 176], [592, 253]]
        "CH03.mp4": [[501, 937], [1125, 794], [730, 338], [346, 334]],     #region video 2: [[501, 937], [1125, 794], [730, 338], [346, 334]]
        "CH04_1.mp4": [[1469, 632], [1106, 534], [244, 1077], [1366, 1077]],   #region video 3: [[1469, 632], [1106, 534], [244, 1077], [1366, 1077]]
        "CH02_1.mp4": [[935, 1068], [1242, 636], [1566, 746], [1397, 1075]],  #region video 4: [[935, 1068], [1242, 636], [1566, 746], [1397, 1075]]
        "CH02_2.mp4": [[589, 1070], [656, 674], [120, 613], [10, 1068]],      #region video 5: [[589, 1070], [656, 674], [120, 613], [10, 1068]]
        "CH04_2.mp4": [[849, 1065], [1407, 400], [1559, 460], [1307, 1075]],  #region video 6: [[849, 1065], [1407, 400], [1559, 460], [1307, 1075]]
    }
    
    video_filename = os.path.basename(video_path)
    current_counting_region_points = counting_region.get(video_filename)
    
    # Check video available
    if current_counting_region_points is None:
        print(f"Not Found '{video_filename}'")
        use_region_counting = False
    else:
        # list of lists to numpy array for cv2.pointPolygonTest
        current_counting_region_points = np.array(current_counting_region_points, np.int32)
        # Reshape for drawing
        current_counting_region_points_for_drawing = current_counting_region_points.reshape((-1, 1, 2))
        use_region_counting = True


    pizza_count = 0
    # trackid for prevent duplicate
    counted_pizza_ids = set()
    frame_count = 0
    while True:
        ret, frame = cap.read() 
        if not ret:
            print("Can not read frame")
            break

        start_frame_time = time.time()

        # run inference in frame
        # results = model(frame, stream=True, conf=confidence_threshold, tracker="bytetrack.yaml")
        results = model.track(frame, persist=True, conf=confidence_threshold, tracker="bytetrack.yaml")
        
        current_frame_pizza_ids = [] # IDs of pizza 

        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()  
            classes_id = r.boxes.cls.cpu().numpy() 
            track_ids = r.boxes.id.cpu().numpy() if r.boxes.id is not None else None 
            print(f"  Raw track_ids from results: {track_ids}")
            confidences = r.boxes.conf.cpu().numpy() 
            print(f"Found {len(boxes)} detections in this frame.") 

            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box)
                cls_id = int(classes_id[i])
                label = model_classes[cls_id]
                conf = confidences[i]
                track_id = track_ids[i] if track_ids is not None else -1
                print(f"Detected: {label} with confidence {conf:.2f}")
                print(f"Track ID: {track_id}")

                # Filter (classes_to_detect)
                if classes_to_detect and label not in classes_to_detect:
                    continue

                # Count logic
                if use_region_counting and track_id != -1:
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    pizza_point = (center_x, center_y) # center of box
                    cv2.circle(frame, pizza_point, 5, (0, 0, 255), -1)

                    region_count = cv2.pointPolygonTest(current_counting_region_points, pizza_point, False)
                    print(f"Pizza ID: {track_id}, Point: {pizza_point}, Test Result: {region_count}")

                    # check center point in polygon
                    if region_count >= 0:
                        if track_id not in counted_pizza_ids:
                            pizza_count += 1
                            counted_pizza_ids.add(track_id)
                            print(f"Đã đếm một pizza mới (ID: {track_id}) trong vùng! Tổng số: {pizza_count}")
                

                current_frame_pizza_ids.append(track_id)
                

                # bbox
                color = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                text_label = f"{label} {conf:.2f}"
                if track_id != -1:
                    text_label = f"ID: {track_id} {text_label}"

                cv2.putText(frame, text_label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Total pizza
        cv2.putText(frame, f"Total Pizzas: {pizza_count}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) # Màu đỏ
        
        # Drawing region count
        if use_region_counting:
            cv2.polylines(frame, [current_counting_region_points_for_drawing], isClosed=True, color=(255, 0, 0), thickness=2) # Màu xanh dương
            cv2.putText(frame, "Counting Region", (current_counting_region_points[0][0], current_counting_region_points[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
        
        # cv2.imshow('Pizza Sales Counter', frame)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        
        #### VideoWriter ####
        out.write(frame)

        end_frame_time = time.time() 
        frame_processing_time = end_frame_time - start_frame_time

        if frame_processing_time > 0:
            processing_fps = 1 / frame_processing_time
        else:
            processing_fps = float('inf')

        frame_count += 1
        print(f"Processed frame {frame_count} | Proc. FPS: {processing_fps:.2f} | Total Pizzas: {pizza_count}", end='\r')


    cap.release()
    out.release() # VideoWriter
    # cv2.destroyAllWindows()
    print(f"Tổng số pizza đã đếm: {pizza_count}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pizza Sales Counting System using YOLOv8 Object Detection.")
    parser.add_argument('--video_path', type=str, required=True,
                        help='link to video')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                        help='model name or .pt file')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='confidence of classification')
    parser.add_argument('--classes', nargs='+', type=str,
                        help='classés to detect, default all classes')

    args = parser.parse_args()

    data_dir = Path('data')
    data_dir.mkdir(parents=True, exist_ok=True)
    if not Path(args.video_path).exists():
        print(f"Error:'{args.video_path}' does not exist")
        print(f"Put video in data'{data_dir}' ")
        print("Ex: python pizza_detector.py --video_path data/your_pizza_video.mp4")
    else:
        detect_pizzas_in_video(
            video_path=args.video_path,
            model_name=args.model,
            confidence_threshold=args.conf,
            classes_to_detect=args.classes
        )