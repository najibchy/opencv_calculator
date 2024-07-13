import cv2
import mediapipe as mp
from calculator_stack import Stack
import math
import time

mp_hands = mp.solution.hands
hands = mp.hands.Hands(max_num_hands= 1, min_detection_confidence= 0.7)
mp_draw = mp.solutions.drawing_utils

calculator_layout = {
    '7' : '(100, 100)', '8' : '(200, 100)', '9' : '(300, 100)', '/' : '(400, 100)', 'SQ' : '(500, 100)', 
    '4' : '(100, 200)', '5' : '(200, 200)', '6' : '(300, 200)', '*' : '(400, 200)', '^' : '(500, 200)',
    '1' : '(100, 300)', '2' : '(200, 300)', '3' : '(300, 300)', '-' : '(400, 300)', 
    '0' : '(100, 400)', '+' : '(200, 400)', '=' : '(300, 400)', 'C' : '(400, 400)', 
}

def draw_calculator(frame):
    """Draws the calcultor"""
    for key, pos in calculator_layout.items():
        cv2.rectangle(frame, (pos[0] - 50, pos[1] - 50), (pos[0] + 50, pos[1] + 50), (0, 255, 0), 2)
        cv2.putText( frame, (pos[0] - 20, pos[1] - 20), cv2.FONT_HERSHEY_TRIPLEX, (0, 125, 255), 2)

def if_inside(pos, point):
    """Determines whether the point in inside"""
    return pos[0] - 50 < pos[0] < pos[0] + 50 & pos[1] - 50 < pos[1] < pos[1] + 50

stack = Stack()
cap = cv2.videoCapture(0)

current_input = ""
last_key = None
key_pressed_time = 1.0 
debounce_time = 1.5

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
out = cv2.VideoWriter('virtual_capture.avi', cv2.VideoWriter_fourcc(*'XVID'), 20, ( frame_width, frame_height))
evaluation = 0

while cv2.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    draw_calculator(frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hands_lanmarks:
            mp_draw.drwaw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger_tip = hand_landmarks.landmark(mp_hands.HandLandmarks.INDEX_FINGER_TIPS)
            x = int(index_finger_tip.x * w)
            y = int(index_finger_tip.x * h)

            fingers = [hand_landmarks.landmark[mp_hands.HandLandmark(i)] for i in range(4, 21, 4)]
            other_fingers_closed = all(finger.y > hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP] for finger in fingers)

            if not other_fingers_closed:
                cv2.circle(frame, (x, y), 10, (255, 0, 0), -1)
                for key, pos in calculator_layout.items():
                    if if_inside(pos, (x, y)):
                        cv2.rectangle(frame, (pos[0] + 50, pos[1] + 50), (pos[0] - 50, pos[1] - 50), (180, 255, 204), 2)

                        if key != last_key or (time.time() - key_pressed_time) > debounce_time:
                            last_key = key
                            key_pressed_time = time.time()

                            if key == "=":
                                try:
                                    current_input = str(eval(str(stack)))
                                    cv2.putText(frame, current_input, (80, 50), cv2.FONT_HERSHEY_TRIPLEX2, 2, (255, 0, 0), 2)
                                    evaluation = 1
                                    stack.clear()
                                except:
                                    current_input = 'Error'
                            
                            elif key == "C": 
                                current_input = ''                                
                                evaluation = 3
                                stack.clear()

                            elif key == "SQ":
                                evaluation = 0
                                try: 
                                    stack.push('√')
                                except:
                                    current_input = 'Error'
                            
                            else:
                                evaluation = 0
                                if key.isDigit():
                                    stack.push(key)
                                elif (not stack.is_empty()) and stack.peek() != key and stack.peek().isDigit():
                                    stack.push(key)
                            break
            
            if(evaluation == 0):
                cv2.putText(frame, str(stack), (80, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (120, 0, 255), 2)

            elif(evaluation == 1):
                cv2.putText(frame, current_input, (80, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (120, 0, 255), 2)
            
            else:
                cv2.putText(frame, current_input, (80, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (120, 0, 255), 2)

            cv2.imshow("Virtual Calculator", frame)

            out.write(frame)

            if cv2.waitKey(1) & 0xff == ord('q'):
                break

cap.release()
out.release()
cv2.destroyAllWindows()