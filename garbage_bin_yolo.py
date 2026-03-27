import cv2
import torch

# -----------------------------
# Configuration
# -----------------------------
CAMERA_INDEX = 1
CONF_THRESH = 0.25
ALIGN_THRESHOLD = 25  # pixels of deadband

FORWARD = 0
BACKWARD = 1
STOP = 2


def get_box_center_xyxy(box):
    """
    box: [xmin, ymin, xmax, ymax]
    returns (cx, cy)
    """
    x1, y1, x2, y2 = box
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)
    return cx, cy


def compute_command(trash_x, object_x, threshold=ALIGN_THRESHOLD):
    """
    Compare the object's horizontal position with the trash can's.
    
    Returns:
        0 = forward
        1 = backward
        2 = stop
    """
    error = object_x - trash_x

    if error > threshold:
        return FORWARD
    elif error < -threshold:
        return BACKWARD
    else:
        return STOP


def pick_two_best_detections(results_df, conf_thresh=CONF_THRESH):
    """
    From YOLO results, keep detections above threshold and return the top 2 by confidence.
    """
    if results_df is None or len(results_df) == 0:
        return []

    filtered = results_df[results_df["confidence"] >= conf_thresh].copy()
    if len(filtered) < 2:
        return []

    filtered = filtered.sort_values(by="confidence", ascending=False)
    top2 = filtered.head(2)
    return top2.to_dict(orient="records")


def assign_object_and_trashcan(detections):
    """
    Given exactly 2 detections, assign:
    - higher one (smaller cy) -> flying object
    - lower one (larger cy) -> trash can
    """
    d1, d2 = detections

    _, cy1 = get_box_center_xyxy([d1["xmin"], d1["ymin"], d1["xmax"], d1["ymax"]])
    _, cy2 = get_box_center_xyxy([d2["xmin"], d2["ymin"], d2["xmax"], d2["ymax"]])

    if cy1 < cy2:
        flying_object = d1
        trash_can = d2
    else:
        flying_object = d2
        trash_can = d1

    return flying_object, trash_can


def draw_detection(frame, det, label, color):
    x1 = int(det["xmin"])
    y1 = int(det["ymin"])
    x2 = int(det["xmax"])
    y2 = int(det["ymax"])
    conf = float(det["confidence"])

    cx, cy = get_box_center_xyxy([x1, y1, x2, y2])

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.circle(frame, (cx, cy), 5, color, -1)
    cv2.putText(
        frame,
        f"{label} {conf:.2f}",
        (x1, max(20, y1 - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2,
    )

    return cx, cy


def main():
    # Load pretrained YOLOv5 model from PyTorch Hub
    model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
    model.conf = CONF_THRESH

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame.")
            break

        # Run detection
        results = model(frame)

        # Convert predictions to pandas DataFrame
        df = results.pandas().xyxy[0]

        command = STOP

        # Pick two best detections
        detections = pick_two_best_detections(df, CONF_THRESH)

        if len(detections) == 2:
            flying_obj, trash_can = assign_object_and_trashcan(detections)

            obj_x, obj_y = draw_detection(frame, flying_obj, "Flying Object", (0, 0, 255))
            trash_x, trash_y = draw_detection(frame, trash_can, "Trash Can", (0, 255, 0))

            # Draw line between centers
            cv2.line(frame, (obj_x, obj_y), (trash_x, trash_y), (255, 255, 0), 2)

            command = compute_command(trash_x, obj_x)

            cv2.putText(
                frame,
                f"Object x: {obj_x}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            cv2.putText(
                frame,
                f"Trash x: {trash_x}",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
        else:
            cv2.putText(
                frame,
                "Need exactly 2 detections",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )

        command_text = {0: "FORWARD", 1: "BACKWARD", 2: "STOP"}[command]
        cv2.putText(
            frame,
            f"Command: {command_text} ({command})",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        # Replace this print with serial/motor output later
        print(command)

        cv2.imshow("Trash Can Catcher", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()