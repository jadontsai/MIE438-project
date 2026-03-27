import cv2
from ultralytics import YOLO

# -----------------------------
# Configuration
# -----------------------------
CAMERA_INDEX = 1
CONF_THRESH = 0.25
ALIGN_THRESHOLD = 25  # pixels

FORWARD = 0
BACKWARD = 1
STOP = 2


def get_box_center_xyxy(box):
    x1, y1, x2, y2 = box
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)
    return cx, cy


def compute_command(trash_x, object_x, threshold=ALIGN_THRESHOLD):
    error = object_x - trash_x

    if error > threshold:
        return FORWARD
    elif error < -threshold:
        return BACKWARD
    else:
        return STOP


def pick_two_best_detections(boxes, confs):
    """
    boxes: list of [x1,y1,x2,y2]
    confs: list of confidence values
    """
    if len(boxes) < 2:
        return []

    # sort by confidence
    idxs = sorted(range(len(confs)), key=lambda i: confs[i], reverse=True)
    top2 = idxs[:2]

    return [(boxes[i], confs[i]) for i in top2]


def assign_object_and_trashcan(detections):
    (box1, conf1), (box2, conf2) = detections

    _, cy1 = get_box_center_xyxy(box1)
    _, cy2 = get_box_center_xyxy(box2)

    if cy1 < cy2:
        return (box1, conf1), (box2, conf2)
    else:
        return (box2, conf2), (box1, conf1)


def draw_detection(frame, box, conf, label, color):
    x1, y1, x2, y2 = map(int, box)
    cx, cy = get_box_center_xyxy(box)

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
    # Load YOLOv8 model (small, fast)
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame.")
            break

        results = model(frame, conf=CONF_THRESH, verbose=False)

        command = STOP

        # Extract detections
        boxes = []
        confs = []

        if len(results[0].boxes) > 0:
            for box in results[0].boxes:
                b = box.xyxy[0].cpu().numpy()
                c = float(box.conf[0].cpu().numpy())

                boxes.append(b)
                confs.append(c)

        detections = pick_two_best_detections(boxes, confs)

        if len(detections) == 2:
            flying_obj, trash_can = assign_object_and_trashcan(detections)

            obj_x, obj_y = draw_detection(
                frame, flying_obj[0], flying_obj[1], "Flying Object", (0, 0, 255)
            )
            trash_x, trash_y = draw_detection(
                frame, trash_can[0], trash_can[1], "Trash Can", (0, 255, 0)
            )

            cv2.line(frame, (obj_x, obj_y), (trash_x, trash_y), (255, 255, 0), 2)

            command = compute_command(trash_x, obj_x)

            cv2.putText(frame, f"Object x: {obj_x}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.putText(frame, f"Trash x: {trash_x}", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        else:
            cv2.putText(frame, "Need 2 detections", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        command_text = {0: "FORWARD", 1: "BACKWARD", 2: "STOP"}[command]

        cv2.putText(frame, f"Command: {command_text} ({command})",
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        print(command)

        cv2.imshow("Trash Can Catcher (YOLOv8)", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()