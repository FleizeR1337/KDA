import cv2
import mediapipe as mp
import random
import time
import json
import pygame

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Open a video stream from the webcam with higher resolution
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Set width to 1280 pixels
cap.set(4, 1080)  # Set height to 720 pixels

# Initialize game parameters
score = 0
best_score = 0
previous_score = 0
ball_x = random.randint(50, 1230)  # Adjusted for the larger frame size
ball_y = random.randint(50, 670)   # Adjusted for the larger frame size
ball_radius = 30  # Увеличенный хит бокс для руки

# Load previous best and previous scores if available
try:
    with open('best_score.json', 'r') as file:
        best_score_data = json.load(file)
        best_score = best_score_data['best_score']
        previous_score = best_score_data['previous_score']
except FileNotFoundError:
    # If the file is not found, initialize scores to 0
    best_score = 0
    previous_score = 0

# Initialize game duration (in seconds)
game_duration = 30  # You can adjust the game duration as needed
start_time = 0.0  # Initialize start_time to 0.0

# Flag to determine if the game is on the start screen
on_start_screen = True

# Initialize pygame and load background music
pygame.init()
pygame.mixer.init()
background_music = pygame.mixer.Sound('background_music.mp3')  # Замените 'background_music.wav' на путь к вашему аудиофайлу

# Индексы ландмарок на правой и левой ладонях
right_hand_landmarks = [mp_pose.PoseLandmark.RIGHT_PINKY,
                        mp_pose.PoseLandmark.LEFT_WRIST,
                        mp_pose.PoseLandmark.RIGHT_ANKLE,
                        mp_pose.PoseLandmark.RIGHT_INDEX,
                        mp_pose.PoseLandmark.RIGHT_THUMB]

left_hand_landmarks = [mp_pose.PoseLandmark.LEFT_PINKY,
                       mp_pose.PoseLandmark.LEFT_WRIST,
                       mp_pose.PoseLandmark.LEFT_ANKLE,
                       mp_pose.PoseLandmark.LEFT_INDEX,
                       mp_pose.PoseLandmark.LEFT_THUMB]

while True:
    ret, frame = cap.read()

    if not ret:
        continue

    # Flip the frame horizontally (mirror reflection)
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB format
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    try:
        # Detect and track body pose on the frame
        results = pose.process(frame_rgb)
    except Exception as e:
        print("Error processing frame:", e)
        continue  # Skip this frame and continue with the next one

    # Detect and track body pose on the frame
    results = pose.process(frame_rgb)

    # Check if the game has started
    if on_start_screen:
        # Display start screen with initial best and previous scores
        cv2.putText(frame, "Touch the Jerry to start the game", (300, 400), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255), 2)
        cv2.putText(frame, f'Best Score: {best_score}', (400, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f'Previous Score: {previous_score}', (400, 500), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255), 2)
        cv2.imshow('Body Tracking Game', frame)

        if results.pose_landmarks:
            # Check if any of the right hand landmarks are in proximity to the red ball
            for landmark in right_hand_landmarks:
                landmark_x = int(results.pose_landmarks.landmark[landmark].x * frame.shape[1])
                landmark_y = int(results.pose_landmarks.landmark[landmark].y * frame.shape[0])

                if ((landmark_x - ball_x) ** 2 + (landmark_y - ball_y) ** 2) ** 0.5 < ball_radius:
                    on_start_screen = False
                    start_time = time.time()
                    score = 0
                    background_music.play()  # Воспроизведение музыки на задний фон

    else:
        # Calculate game duration
        elapsed_time = time.time() - start_time
        remaining_time = max(0, game_duration - int(elapsed_time))

        if elapsed_time < game_duration:
            # Game is still ongoing
            if results.pose_landmarks:
                # Draw lines to visualize body pose
                mp_drawing = mp.solutions.drawing_utils
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Check if any of the right hand landmarks are in proximity to the red ball
                for landmark in right_hand_landmarks:
                    landmark_x = int(results.pose_landmarks.landmark[landmark].x * frame.shape[1])
                    landmark_y = int(results.pose_landmarks.landmark[landmark].y * frame.shape[0])

                    if ((landmark_x - ball_x) ** 2 + (landmark_y - ball_y) ** 2) ** 0.5 < ball_radius:
                        # Caught the ball, increase the score and move the ball
                        score += 1
                        ball_x = random.randint(80, 1200)  # Adjusted for the larger frame size
                        ball_y = random.randint(80, 640)   # Adjusted for the larger frame size

                # Check if any of the left hand landmarks are in proximity to the red ball
                for landmark in left_hand_landmarks:
                    landmark_x = int(results.pose_landmarks.landmark[landmark].x * frame.shape[1])
                    landmark_y = int(results.pose_landmarks.landmark[landmark].y * frame.shape[0])

                    if ((landmark_x - ball_x) ** 2 + (landmark_y - ball_y) ** 2) ** 0.5 < ball_radius:
                        # Caught the ball, increase the score and move the ball
                        score += 1
                        ball_x = random.randint(80, 1200)  # Adjusted for the larger frame size
                        ball_y = random.randint(80, 640)   # Adjusted for the larger frame size

            # Display the score, remaining time, and previous scores
            cv2.putText(frame, f'Score: {score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f'Time: {remaining_time}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f'Best Score: {best_score}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f'Previous Score: {previous_score}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                        2)
        else:
            # Game over, calculate best score and save scores
            if score > best_score:
                previous_score = best_score
                best_score = score
                with open('best_score.json', 'w') as file:
                    json.dump({'best_score': best_score, 'previous_score': previous_score}, file)
            else:
                previous_score = score

            # Display end game message and allow restarting
            cv2.putText(frame, "End Game. Touch the boll to play again", (300, 400), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2)

            # Check if any of the right hand landmarks or left hand landmarks are in proximity to the red ball
            for landmark in right_hand_landmarks:
                landmark_x = int(results.pose_landmarks.landmark[landmark].x * frame.shape[1])
                landmark_y = int(results.pose_landmarks.landmark[landmark].y * frame.shape[0])

                if ((landmark_x - ball_x) ** 2 + (landmark_y - ball_y) ** 2) ** 0.5 < ball_radius:
                    on_start_screen = True
                    start_time = 0.0  # Reset start_time
                    score = 0  # Reset score
                    ball_x = random.randint(50, 1230)  # Adjusted for the larger frame size
                    ball_y = random.randint(50, 670)   # Adjusted for the larger frame size

            for landmark in left_hand_landmarks:
                landmark_x = int(results.pose_landmarks.landmark[landmark].x * frame.shape[1])
                landmark_y = int(results.pose_landmarks.landmark[landmark].y * frame.shape[0])

                if ((landmark_x - ball_x) ** 2 + (landmark_y - ball_y) ** 2) ** 0.5 < ball_radius:
                    on_start_screen = True
                    start_time = 0.0  # Reset start_time
                    score = 0  # Reset score
                    ball_x = random.randint(50, 1230)  # Adjusted for the larger frame size
                    ball_y = random.randint(50, 670)   # Adjusted for the larger frame size

    # Display the ball
    cv2.circle(frame, (ball_x, ball_y), ball_radius, (0, 0, 255), -1)  # Red ball

    # Display the frame with pose tracking and the ball
    cv2.imshow('Body Tracking Game', frame)

    # Exit the loop when the 'q' key is pressed
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

cap.release()  # Release the video capture object
pose.close()   # Close the MediaPipe Pose model

# Stop background music and close windows
background_music.stop()
pygame.mixer.quit()
pygame.quit()
cv2.destroyAllWindows()
