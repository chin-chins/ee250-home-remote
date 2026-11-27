# Gesture-Controlled Remote: Two-Week Build Schedule

**Dates:** November 24–December 7, 2026  
**Main priority:** Reliable gesture-controlled music playback and physical light control.  
**Stretch feature:** Temperature control, with a local demonstration as backup and Nest integration optional.

## Team responsibilities

- **Person A:** C firmware using ESP-IDF for both ESP32s; IMU sampling; MQTT communication; LED control; optional temperature sensor.
- **Person B:** Python server; gesture recording and DTW recognition; mode and action logic; browser music player; web dashboard.
- **Both:** System design, gesture-data collection, integration, evaluation, documentation, and presentation. Each person should understand the entire system.

## Core system

Remote ESP32 + IMU → MQTT → Python gesture recognition and mode logic → browser music player / output ESP32 + LED.

| Gesture | Music mode | Light mode |
| --- | --- | --- |
| Switch mode | Switch to Light | Switch to Music |
| Increase | Increase player volume | Increase LED brightness |
| Decrease | Decrease player volume | Decrease LED brightness |
| Toggle | Play/pause | Turn light on/off |

The dashboard highlights the active mode and shows the latest recognized gesture, connection status, and applied output state. Keep Temperature out of the mode cycle until it is implemented.

## Day 1 — Tuesday, November 24: Setup and agreement

### Person A
- [ ] Verify C build, upload, and serial logging with ESP-IDF on both ESP32s.
- [ ] Check available IMU, LED, resistor, cables, wires, and breadboards.
- [ ] Order or borrow missing essential parts immediately.
- [ ] Connect the IMU if available.

### Person B
- [ ] Set up the Python environment and local MQTT broker.
- [ ] Create the Python server and basic dashboard.
- [ ] Add the shared project to version control.

### Together
- [ ] Choose four distinct gestures and agree how users start and end a gesture.
- [ ] Agree MQTT topics and message fields, including timestamps, sequence numbers, sample units, and window length.
- [ ] Agree initial mode, adjustment step sizes, and output limits.

## Day 2 — Wednesday, November 25: Sensor readings

### Person A
- [ ] Read accelerometer and gyroscope values over I²C in C.
- [ ] Sample at a consistent rate and timestamp readings.
- [ ] Verify axis directions, units, and stationary readings.

### Person B
- [ ] Build the MQTT receiver for motion data.
- [ ] Prepare sample messages so server work can continue before hardware is ready.
- [ ] Add basic recording and connection-status displays.

### Together
- [ ] Confirm real sensor samples reach the laptop.

## Day 3 — Thursday, November 26: Motion windows and dataset

### Person A
- [ ] Buffer samples into motion windows.
- [ ] Publish windows over Wi-Fi/MQTT with sequence numbers.
- [ ] Log missing samples and connection errors.

### Person B
- [ ] Save labeled gesture windows with performer and session identifiers.
- [ ] Plot recorded signals to identify empty, clipped, or inconsistent windows.
- [ ] Separate training recordings from evaluation recordings.

### Together
- [ ] Record initial examples of every gesture from both people.
- [ ] Record idle periods and ordinary movements for rejection testing.
- [ ] Check that recordings and labels are usable before collecting more.

## Day 4 — Friday, November 27: Independent output controls

### Person A
- [ ] Connect an ordinary LED through a current-limiting resistor to the output ESP32.
- [ ] Implement LED on/off and PWM brightness control in C.
- [ ] Test minimum and maximum brightness locally.

### Person B
- [ ] Build browser playback using local audio files.
- [ ] Add manual play/pause and player-volume controls.
- [ ] Add dashboard controls for sending test light commands.

### Together
- [ ] Verify music and light control independently of gesture recognition.

## Day 5 — Saturday, November 28: First recognizer

### Person A
- [ ] Receive light commands over MQTT.
- [ ] Validate commands and apply brightness limits.
- [ ] Publish the LED state after applying a command.

### Person B
- [ ] Implement consistent motion preprocessing for training and live data.
- [ ] Implement a baseline DTW gesture recognizer.
- [ ] Route predictions from saved windows to action messages in a test mode.

### Together
- [ ] Confirm saved gesture windows produce the expected actions.
- [ ] Identify the most commonly confused gestures.

## Day 6 — Sunday, November 29: Live music control

### Person A
- [ ] Stabilize window timing and continuous motion transmission.
- [ ] Verify the IMU is mounted firmly relative to the remote.
- [ ] Diagnose missing or delayed windows during live use.

### Person B
- [ ] Connect live motion windows to the DTW recognizer.
- [ ] Connect recognized commands to browser music playback.
- [ ] Show the latest gesture and action on the dashboard.

### Together
- [ ] Demonstrate live gesture-controlled play/pause and volume changes.
- [ ] Collect additional examples where recognition fails.

## Day 7 — Monday, November 30: Mode switching and lights

### Person A
- [ ] Verify live gesture commands change the physical LED.
- [ ] Confirm the reported LED state matches the actual output.

### Person B
- [ ] Implement server-owned Music/Light mode switching.
- [ ] Highlight the active mode prominently on the dashboard.
- [ ] Reuse increase, decrease, and toggle gestures according to the active mode.
- [ ] Keep music-player state and dashboard state synchronized.

### Together
- [ ] Complete a live Music → Light → Music demonstration.
- [ ] Verify a mode-switch gesture does not also adjust an output.

## Day 8 — Tuesday, December 1: Reliability

### Person A
- [ ] Add Wi-Fi/MQTT reconnection behavior.
- [ ] Report remote and output-node connection status.
- [ ] Check for resets, loose connections, and power problems.

### Person B
- [ ] Reject uncertain or unrelated motion windows.
- [ ] Add a cooldown or equivalent handling to prevent repeated actions from one gesture.
- [ ] Enforce volume and brightness limits.
- [ ] Show disconnected or failed actions clearly.

### Together
- [ ] Test ordinary movement for accidental commands.
- [ ] Confirm users can tell whether a command succeeded.

## Day 9 — Wednesday, December 2: Core-feature checkpoint

### Person A
- [ ] Test both ESP32s across power cycles and reconnections.
- [ ] Run a longer session to check device stability.

### Person B
- [ ] Evaluate recognition on fresh attempts excluded from training.
- [ ] Record per-gesture results and common confusions.
- [ ] Measure approximate gesture-to-action delay and accidental-trigger rate.

### Together
- [ ] Verify reliable music play/pause and volume control.
- [ ] Verify reliable physical LED on/off and brightness control.
- [ ] Verify reliable mode switching and accurate dashboard feedback.
- [ ] Decide whether the core is stable enough to attempt temperature.

**Decision:** If core features remain unreliable, use Days 10–11 for fixes and omit temperature.

## Day 10 — Thursday, December 3: Core fixes or optional temperature

### Person A
- [ ] Fix the highest-impact firmware or hardware issues.
- [ ] If the core checkpoint passed, connect an available temperature sensor to the output ESP32.
- [ ] If using a sensor, read and publish measured temperature in C.

### Person B
- [ ] Fix the highest-impact recognition, player, or dashboard issues.
- [ ] If time allows, check Nest model support, account access, registration cost, and authorization requirements.
- [ ] Define one temperature interface that can use either local-demo state or Nest state.

### Together
- [ ] Time-box Nest exploration; stop if setup threatens the main project.
- [ ] Choose local temperature demo, local demo plus Nest, or no temperature feature.

## Day 11 — Friday, December 4: Optional local demo and feature freeze

### Person A
- [ ] If adding temperature, verify sensor readings and optional heating/cooling indicator LEDs.
- [ ] Secure wiring and mount the remote components.
- [ ] If temperature is omitted, spend the day on core reliability and physical polish.

### Person B
- [ ] If adding temperature, implement gesture-adjusted setpoint and measured-temperature display.
- [ ] Add a deadband and clearly label local heating/cooling requests as simulated.
- [ ] If Nest access already works and the local demo is complete, add bounded setpoint commands and confirmed/pending/error feedback.
- [ ] Keep Nest credentials on the server and out of version control.
- [ ] Ensure the local demo can be selected if Nest or internet access fails.

### Together
- [ ] Run the complete core demo several times.
- [ ] Verify any optional feature is dependable enough to include.
- [ ] Freeze features; remove unfinished modes from the demo flow.

## Day 12 — Saturday, December 5: Documentation and final testing

### Person A
- [ ] Draft hardware, C firmware, wiring, and communication descriptions.
- [ ] Write build, flash, and hardware-startup instructions.
- [ ] Document exact ESP32 and sensor models and pin assignments.

### Person B
- [ ] Draft gesture dataset, DTW, dashboard, and music-control descriptions.
- [ ] Document Python dependencies and server startup.
- [ ] Summarize evaluation results, limitations, and failure handling.

### Together
- [ ] Assemble the labeled system block diagram.
- [ ] Complete the write-up within the assignment's two-page limit.
- [ ] Complete the README with names, execution instructions, and external libraries.
- [ ] Acknowledge AI assistance in the write-up and relevant code comments.
- [ ] Run the system from a fresh start using only the written instructions.

## Day 13 — Sunday, December 6: Video and rehearsal

### Person A
- [ ] Prepare to explain sampling, I²C, MQTT, C firmware, and PWM.
- [ ] Review the Python recognition and application logic.

### Person B
- [ ] Prepare to explain DTW, training/evaluation separation, rejection, and mode logic.
- [ ] Review both ESP32s' firmware and wiring.

### Together
- [ ] Rehearse the main sequence: play music → adjust volume → switch mode → turn on LED → change brightness.
- [ ] Include temperature only after the main sequence, if complete.
- [ ] Record the narrated demonstration video within the four-minute limit.
- [ ] Upload the video and verify its public link works while signed out.
- [ ] Rehearse design questions and limitations.
- [ ] Check the announced in-person demo arrangements separately from the submission deadline.

## Day 14 — Monday, December 7: Submission

### Person A
- [ ] Verify firmware source, pin documentation, and hardware operation.
- [ ] Pack the remote, output node, cables, and available spares for the demo.

### Person B
- [ ] Verify Python/web source, dependencies, and needed model/template files are included.
- [ ] Verify the final write-up, README, and video link.
- [ ] Check the submission package contains no credentials or private tokens.

### Together
- [ ] Perform one final fresh-start core demonstration.
- [ ] Check the assignment and submission portal for required filenames, formats, and exact cutoff time.
- [ ] Submit all required deliverables and verify successful submission.
- [ ] Complete the individual teamwork assessments when available.

## Scope rules

- [ ] Prioritize music, physical lights, mode feedback, and reliable recognition over optional features.
- [ ] Use DTW first; consider another model only if the core works and evaluation justifies the change.
- [ ] Keep manual dashboard controls available for troubleshooting.
- [ ] Keep the core music/light demo operational without cloud access.
- [ ] Use the local temperature demonstration as the Nest fallback, if temperature is included.
- [ ] Label simulated HVAC behavior honestly; a sensor or LED does not change room temperature.
- [ ] Add no new features after December 4.
