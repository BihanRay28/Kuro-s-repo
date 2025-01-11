import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import chess

# Initialize chessboard and session state
if "chess_board" not in st.session_state:
    st.session_state.chess_board = chess.Board()

# Reset game function
def reset_game():
    st.session_state.chess_board = chess.Board()

# Map FEN piece symbols to sprite names
PIECE_SPRITES = {
    "K": "white_king.png",
    "Q": "white_queen.png",
    "R": "white_rook.png",
    "B": "white_bishop.png",
    "N": "white_knight.png",
    "P": "white_pawn.png",
    "k": "black_king.png",
    "q": "black_queen.png",
    "r": "black_rook.png",
    "b": "black_bishop.png",
    "n": "black_knight.png",
    "p": "black_pawn.png",
}

CHESSBOARD_PATH = "rect-8x8.png"

# Function to render the chessboard with pieces and labels
def render_chessboard_with_labels():
    board = Image.open(CHESSBOARD_PATH).convert("RGBA")
    board_width, board_height = board.size
    square_size = board_width // 8

    # Extend the image to make room for labels
    margin = square_size // 4
    extended_width = board_width + margin
    extended_height = board_height + margin
    extended_board = Image.new("RGBA", (extended_width, extended_height), "white")
    extended_board.paste(board, (margin, 0))

    # Add labels (rank and file)
    draw = ImageDraw.Draw(extended_board)
    font_size = square_size // 4
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Draw ranks (numbers) on the left side
    for row in range(8):
        label = str(8 - row)
        x = margin // 4
        y = row * square_size + (square_size - font_size) // 2
        draw.text((x, y), label, fill="black", font=font)

    # Draw files (letters) at the bottom
    for col in range(8):
        label = chr(ord("a") + col)
        x = col * square_size + margin + (square_size - font_size) // 2
        y = board_height + margin // 8
        draw.text((x, y), label, fill="black", font=font)

    # Draw pieces based on FEN
    for square in chess.SQUARES:
        piece = st.session_state.chess_board.piece_at(square)
        if piece:
            sprite_path = PIECE_SPRITES[piece.symbol()]
            piece_image = Image.open(sprite_path).resize((square_size, square_size)).convert("RGBA")

            # Calculate position (FEN starts from a1 at the bottom left)
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            x, y = col * square_size + margin, row * square_size
            extended_board.paste(piece_image, (x, y), piece_image)

    return extended_board

# Function to handle moves
def handle_move(from_square, to_square):
    try:
        from_index = chess.parse_square(from_square)
        to_index = chess.parse_square(to_square)
        move = chess.Move(from_index, to_index)
        if move in st.session_state.chess_board.legal_moves:
            st.session_state.chess_board.push(move)
            return "Move successful!", "success"
        else:
            return "Illegal move! Try again.", "error"
    except ValueError:
        return "Invalid square entered. Use standard algebraic notation (e.g., 'e2', 'e4').", "error"

# Check if game is over
if st.session_state.chess_board.is_game_over():
    st.title("CHECKMATE!!!!")
    result = st.session_state.chess_board.result()
    if result == "1-0":
        winner = "White"
    elif result == "0-1":
        winner = "Black"
    else:
        winner = "Draw"
    st.subheader(f"Team {winner} wins!")

    if st.button("Start New Game"):
        reset_game()
        st.session_state.clear()  # Clear session state to reset the game
else:
    # Streamlit app layout
    st.title("Chess Game")
    st.write(f"Current Turn: *{'White' if st.session_state.chess_board.turn else 'Black'}*")

    # Render chessboard with labels
    board_image = render_chessboard_with_labels()
    st.image(board_image, caption="Chessboard", use_container_width=True)

    # Form for move input
    with st.form("move_form"):
        from_square = st.text_input("Enter the square of the piece you want to move (e.g., 'e2'):", key="from_square")
        to_square = st.text_input("Enter the square where you want to move the piece (e.g., 'e4'):", key="to_square")
        submit = st.form_submit_button("Submit Move")

    # Handle move submission
    if submit:
        message, status = handle_move(from_square, to_square)
        if status == "success":
            st.success(message)
        else:
            st.error(message)
