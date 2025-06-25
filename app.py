import chess
import chess.svg
import streamlit as st
import google.generativeai as genai

# Config and state
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "move_history" not in st.session_state:
    st.session_state.move_history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

st.title("Agent White vs Agent Black")

# Sidebar for API key
st.sidebar.title("Gemini Configuration")
api_key = st.sidebar.text_input("Enter Gemini API key:", type="password")
if api_key:
    st.session_state.gemini_api_key = api_key
    genai.configure(api_key=api_key)
    st.sidebar.success("API key saved!")

max_turns = st.sidebar.number_input("Max number of turns", 1, 100, 10)

def available_moves():
    return [str(move) for move in st.session_state.board.legal_moves]

def ask_gemini(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def get_move_from_agent(agent_name):
    board_fen = st.session_state.board.fen()
    moves = available_moves()
    prompt = f"""
You are a professional chess player ({agent_name}).
The board is currently:
FEN: {board_fen}
Available legal moves are: {', '.join(moves)}
Reply with only one move in UCI format (e.g., e2e4). No explanation.
"""
    response = ask_gemini(prompt)
    return response.split()[0]  # Return the first word as move

def play_turn():
    agent = "White" if st.session_state.board.turn == chess.WHITE else "Black"
    move_str = get_move_from_agent(f"Agent {agent}")
    try:
        move = chess.Move.from_uci(move_str)
        if move in st.session_state.board.legal_moves:
            st.session_state.board.push(move)
            st.session_state.turn_count += 1
            board_svg = chess.svg.board(st.session_state.board, size=400,
                                        arrows=[(move.from_square, move.to_square)],
                                        fill={move.from_square: "gray"})
            st.session_state.move_history.append((agent, board_svg))
        else:
            st.error(f"Invalid move suggested: {move_str}")
    except:
        st.error(f"Failed to parse move from {agent}: {move_str}")

if st.session_state.gemini_api_key:
    st.subheader("Board")
    st.image(chess.svg.board(st.session_state.board, size=400))

    if st.button("Start Game"):
        st.session_state.board.reset()
        st.session_state.move_history = []
        st.session_state.turn_count = 0
        while not st.session_state.board.is_game_over() and st.session_state.turn_count < max_turns:
            play_turn()

        result = "Game over: "
        if st.session_state.board.is_checkmate():
            result += "Checkmate."
        elif st.session_state.board.is_stalemate():
            result += "Stalemate."
        elif st.session_state.board.is_insufficient_material():
            result += "Draw due to insufficient material."
        else:
            result += "Turn limit reached."
        st.success(result)

        st.subheader("Move History")
        for i, (agent, svg) in enumerate(st.session_state.move_history):
            st.write(f"Move {i + 1} by {agent}")
            st.image(svg)

    if st.button("Reset Game"):
        st.session_state.board.reset()
        st.session_state.move_history = []
        st.session_state.turn_count = 0
        st.success("Game reset!")
else:
    st.warning("Enter your Gemini API key in the sidebar.")