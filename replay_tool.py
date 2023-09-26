import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button
import struct
import sys

start_tick = 0
num_time_steps = 0
timestamps = []
player_datas = []

def load_replay_file(path):
    global start_tick
    global timestamps
    global num_time_steps

    local_spawned = False
    local_spawn_tick = 0

    with open(path, "rb") as file:
        start_tick = struct.unpack("<I", file.read(4))[0]
        print("StartTick: %i\n" % start_tick)

        num_time_steps = 0
        while True:

            # Timestamp
            timestamp_bytes = file.read(4)
            if timestamp_bytes == '' or len(timestamp_bytes) != 4:
                print("Read whole file, exiting...")
                break
        
            timestamp = struct.unpack("<I", timestamp_bytes)[0]
            print("Timestamp: %i\n" % timestamp)

            local_x, local_y, local_z = struct.unpack("fff", file.read(12))
            print("LocalPos: %f, %f, %f\n" % (local_x, local_y, local_z))
            
            if local_x != 0 and local_y != 0 and local_z != 0 and local_spawned == False:
                local_spawned = True
                local_spawn_tick = timestamp

            if round(local_y) == -9999:
                print("detected dead localplayer??")
                break
            
            if local_spawned == True:
                timestamps.append(timestamp - local_spawn_tick)        

            # Ignore local player IsAI/IsScav
            file.read(2)

            # fill player datas of current time step, first entry is always local
            cur_step_data = []
            if local_spawned == True:
                cur_step_data.append([local_x, local_y, local_z, False, False])

            # Now read number of players
            player_nums = struct.unpack(">H", b"\x00" + file.read(1))[0]
            print("player_nums: %i" % player_nums)

            for i in range(player_nums):
                
                # read origin, isAI & isScav
                player_x, player_y, player_z = struct.unpack("fff", file.read(12))
                is_ai, is_scav = struct.unpack("??", file.read(2))

                print("[%i] Player Pos: %f, %f, %f, AI: %r, Scav: %r\n" % 
                      (i, player_x, player_y, player_z, is_ai, is_scav))
                
                if local_spawned == True:
                    cur_step_data.append([player_x, player_y, player_z, is_ai, is_scav])
            
            if local_spawned == True:
                player_datas.append(cur_step_data)
                num_time_steps += 1
                

load_replay_file("test_replay.replay")
print("timesteps: %i" % num_time_steps)

# Create a function to update the 3D plot based on the selected time
min_x = 0
max_x = 0
min_y = 0
max_y = 0
min_z = 0
max_z = 0
def update_plot(val):

    global min_x
    global max_x
    global min_y
    global max_y
    global min_z
    global max_z

    time_index = int(slider.val)
    ax.cla()  # Clear the current plot

    # Plot players as dots at their positions
    colors = ['b', 'g', 'r']

    for player in range(len(player_datas[time_index])):
        x, y, z, is_ai, is_scav = player_datas[time_index][player] 

        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
        if z < min_z:
            min_z = z
        if z > max_z:
            max_z = z

        label_name = ''
        color = ''
        if player == 0:
            label_name = "Local"
            color = 'g'
        else:
            if is_ai == True:
                label_name = f"AI"
                color = 'b'
            elif is_scav == True:
                label_name = f"Player SCAV"
                color = 'r'
            else:
                label_name = f"PMC"
                color = 'r'
                

        ax.scatter(x, y, z, c=color, s=100, marker='o', label=label_name)

    ax.set_title(f'Time: {timestamps[time_index]} ms')
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_zlim(min_z, max_z)
    ax.legend(loc='upper left')
    plt.draw()

# Create a matplotlib figure and 3D axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create a slider for controlling time
axcolor = 'lightgoldenrodyellow'
ax_slider = plt.axes([0.2, 0.02, 0.65, 0.03], facecolor=axcolor)
slider = Slider(ax_slider, 'Time', 0, num_time_steps - 1, valinit=0, valstep=1)

# Create play and stop buttons
ax_play = plt.axes([0.1, 0.02, 0.1, 0.03])
ax_stop = plt.axes([0.01, 0.02, 0.08, 0.03])
button_play = Button(ax_play, 'Play', color=axcolor, hovercolor='0.975')
button_stop = Button(ax_stop, 'Stop', color=axcolor, hovercolor='0.975')

# Variable to control animation state
playing = False

# Define play and stop button actions
def play_animation(event):
    global playing
    if not playing:
        playing = True
        for i in range(num_time_steps):
            if playing:
                slider.set_val(i)
                plt.pause(0.05)  # Delay between time steps
            else:
                break

def stop_animation(event):
    global playing
    playing = False

# Attach button actions
button_play.on_clicked(play_animation)
button_stop.on_clicked(stop_animation)

# Attach the slider's update function
slider.on_changed(update_plot)

# Show the initial 3D plot
update_plot(0)

plt.show()
exit(0)
