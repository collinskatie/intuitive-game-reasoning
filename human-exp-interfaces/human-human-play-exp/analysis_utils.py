from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os 
from PIL import Image

def compute_utility(draw_resp, win_resp): 
    return (1 - (draw_resp + win_resp)) * (-1) + win_resp

def get_pwin(draw_resp, adv_resp): 
    return ((100 - draw_resp)/100) * (adv_resp/100) * 100

def draw_colored_grid(num_rows, num_cols, color_map=None, label_map=None):
    if color_map is None:
        color_map = {}
    if label_map is None:
        label_map = {}

    fig, ax = plt.subplots()
    for row in range(num_rows):
        for col in range(num_cols):
            cell_id = (row,col)
            color = color_map.get(cell_id, 'white')  # Default color is white
            rect = patches.Rectangle((col, num_rows - row - 1), 1, 1, linewidth=1, edgecolor='black', facecolor=color)
            ax.add_patch(rect)

            # Add label if present in label_map
            if cell_id in label_map:
                ax.text(col + 0.5, num_rows - row - 0.5, str(label_map[cell_id] + 1), 
                        ha='center', va='center', fontsize=10
                        , color="white")

    plt.xlim(0, num_cols)
    plt.ylim(0, num_rows)
    ax.set_aspect('equal', adjustable='box')
    plt.gca().invert_yaxis()
    plt.xticks([])
    plt.yticks([])
    fig.tight_layout()
#     plt.show()
    return fig,ax    


def construct_board(player_move_map, move_order_map, n_rows, n_cols, win_conds, 
                    draw_accepted=None,
                    draw_requests=None,
                    player_colors=None, 
                    player_orders=None,
                    player_judgements=None,
                    game_outcome=None):
    
    if player_colors is None: 
        colors = {1: "blue", 2: "red", 0: "white"}
    else: 
        colors = {order: player_colors[player] for order, player in player_orders.items()}
    
    color_map = {move: colors[player] for move, player in player_move_map.items()}

    if "inf" in str(n_rows) or "inf" in str(n_cols): 
        n_rows = 13
        n_cols=13


    fig, ax = draw_colored_grid(n_rows, n_cols, color_map, move_order_map)

    parsed_win_conds = win_conds.replace(".", ".\n")[:-1]
    title = f"{parsed_win_conds}"
    
    if game_outcome is not None: 
        if player_colors is not None: 
            if game_outcome != "Draw": title += f"\n{player_colors[game_outcome].capitalize()} won"
            else: title+= "\nGame ended in a draw."
    
    if draw_accepted is not None and draw_accepted: title += f"\nEnded from draw request"
    
    if draw_requests is not None: 
        if draw_requests[1] != 0:
            # counter per player
            player_counts = {1: 0, 2: 0}
            # Count occurrences
            for entry in data:
                player = entry[0]
                player_counts[player] += 1
    
    if player_judgements is not None and player_colors is not None:
        for player, color in player_colors.items(): 
            title += f"\n{color.capitalize()} player: {player_judgements[player]}"
                
    ax.set_title(title)#\n{resp}")
    return fig

def format_bold_keys(text):
    try:
        data = json.loads(text)
        formatted_text = ''
        for key, value in data.items():
            formatted_text += f'[B]{key}[/B]: {value}\n'
        return formatted_text
    except json.JSONDecodeError:
        return text
    

def parse_time(timestamp: str) -> float:
    # help from GPT --- note: empirica saves out all the way to nanoseconds! 
    # Strip the 'Z' at the end of the timestamp
    timestamp = timestamp[:-1]
    # Truncate the nanoseconds to microseconds by slicing the string
    if '.' in timestamp:
        timestamp = timestamp[:timestamp.index('.') + 7]
    # Parse the datetime string
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    # Convert the time to seconds since the epoch
    time_in_seconds = dt.timestamp()
    return time_in_seconds

def process_game_moves(all_boards): 
    
    all_boards = np.array(eval(all_boards))
    
    n_rows, n_cols = all_boards[0].shape

    player_move_map = {}
    move_order_map = {}

    prev_board = np.zeros([n_rows, n_cols])

    for round, round_board in enumerate(all_boards):
        round_board = np.array(round_board)
        diff = round_board != prev_board  # Find where the boards differ
        row, col = np.where(diff)  # Get the indices of the differences
        row = int(row[0])
        col = int(col[0]) # only one change per turn
        val = int(round_board[row][col])
        player_move_map[(row, col)] = val
        move_order_map[(row, col)] = round
        prev_board = round_board
        
    return player_move_map, move_order_map


import os
from PIL import Image

def pngs_to_pdf(image_directory='figs/', output_pth="gameplay.pdf", shrink_factor=0.8, quality=85):
    # Convert a directory of PNGs to PDF and shrink images

    # Get a list of all PNG files in the directory
    image_files = [f for f in os.listdir(image_directory) if f.endswith('.png')]

    # Sort the files to ensure they are in the correct order
    image_files.sort()

    # Load the images
    images = [Image.open(os.path.join(image_directory, f)) for f in image_files]

    # Resize the images by the shrink factor
    resized_images = []
    for img in images:
        new_size = (int(img.width * shrink_factor), int(img.height * shrink_factor))
        resized_img = img.resize(new_size, Image.LANCZOS)
        resized_images.append(resized_img)

    # Convert the images to RGB (if they are not already)
    images_rgb = [img.convert('RGB') for img in resized_images]

    # Save the images as a PDF with specified quality
    images_rgb[0].save(output_pth, save_all=True, append_images=images_rgb[1:], quality=quality, optimize=True)

# Example usage:
# pngs_to_pdf(shrink_factor=0.8, quality=85)



def compute_se(vals): 
    return 1.96 * np.std(vals)/(len(vals) ** 0.5)

def compute_se_bars(all_vals): 
    return [compute_se(vals) for vals in all_vals]

def flatten(matrix):
    return [item for row in matrix for item in row]