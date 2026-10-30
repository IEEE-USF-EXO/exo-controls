% Real-time 3D model of the MPU6500 IMU

clear; clc; close all;

%% Configuration
port = "COM7";
baudRate = 115200;
sampleRate = 100;

%% Initialize Hardware & Sensor Fusion Filter (cleans up noise)
try
    device = serialport(port, baudRate); % Initialize serial communication
    flush(device);      % clear any irrelevant data from serial port
catch ME
    error("Could not connect to serial port! Check port name and connection.");
end

% Create filter for IMU
fuse = imufilter('SampleRate', sampleRate);

%% Set Up 3D Visualization
fig = figure('Name', 'Real-Time IMU Orientation', 'NumberTitle', 'off');
ax = axes('Parent', fig);
grid(ax, 'on'); axis(ax, 'equal');
view(ax, 3); xlabel(ax, 'X'); ylabel(ax,'Y'); zlabel(ax, 'Z');
xlim(ax, [-2,2]); ylim(ax, [-2,2]); zlim(ax, [-2,2]);
title(ax, 'Reading IMU Data...');

% Create 3D cuboid to represent IMU
% Center the object at the origin (patch object)
[X, Y, Z] = meshgrid([-1, 1], [-0.5, 0.5], [-0.1, 0.1]);
x_vertices = [X(:), Y(:), Z(:)];
faces = [1 2 3 4; 5 6 8 7; 1 2 6 5; 3 4 8 7; 1 3 7 5; 2 4 8 6];
vertices_orig = [-1 -0.5 -0.1; 1 -0.5 -0.1; 1 0.5 -0.1; -1 0.5 -0.1; -1 -0.5 0.1; 1 -0.5 0.1; 1 0.5 0.1; -1 0.5 0.1];

imuPatch = patch('Vertices', vertices_orig, 'Faces', faces, 'FaceColor', 'cyan', 'FaceAlpha', 0.8, 'Parent', ax);

%% Real-Time Processing Loop
while ishandle(fig)
    % Read only when data is available in buffer
    if device.NumBytesAvailable > 0
        % Read data in format "ax,ay,az,gx,gy,gz"
        dataLine = readline(device);
        parsedData = str2num(dataLine);

        % Ensure all 6 values received
        if numel(parsedData) == 6
            accelData = (parsedData(1:3)) * 9.81; % Multiply g by 9.81 to get m*s^2
            gyroData = deg2rad(parsedData(4:6)); % Convert deg/s to rad/s

            % Step fusion filter to get current 3D Quaternion orientation ?
            orientationQuaternion = fuse(accelData, gyroData);

            % Convert quaternion to 3D Rotation Matrix
            rotMatrix = rotmat(orientationQuaternion, 'frame');

            % Rotate original cuboid vertices to new orientation
            updatedVertices = vertices_orig * rotMatrix;

            % Update 3D graphics
            set(imuPatch, 'Vertices', updatedVertices);
            drawnow limitrate; % Refresh plot efficiently
        end
    end
end

%% Close serial connection
clear device;
disp("Serial connection closed.");
