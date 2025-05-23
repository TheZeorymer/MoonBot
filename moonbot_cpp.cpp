#include <iostream>
#include <vector>
#include <string>
#include <array>
#include <algorithm>
#include <cstdint>

// Simple piece values
constexpr int PAWN = 100;
constexpr int KNIGHT = 320;
constexpr int BISHOP = 330;
constexpr int ROOK = 500;
constexpr int QUEEN = 900;
constexpr int KING = 0;

// Board representation: 0=empty, 1-6=white, 7-12=black
// 1=P, 2=N, 3=B, 4=R, 5=Q, 6=K, 7=p, 8=n, 9=b, 10=r, 11=q, 12=k
using Board = std::array<int, 64>;

struct Move {
    int from;
    int to;
    int promotion; // 0 if not a promotion
};

class MoonBotCpp {
public:
    Board board;
    bool white_to_move;

    MoonBotCpp();
    void set_startpos();
    bool make_move(const Move& move);
    int evaluate_board() const;
    int minimax(int depth, int alpha, int beta, bool maximizing, Move& best_move);
    std::vector<Move> generate_legal_moves() const;
    void print_board() const;
};

MoonBotCpp::MoonBotCpp() {
    set_startpos();
    white_to_move = true;
}

void MoonBotCpp::set_startpos() {
    // 1=P, 2=N, 3=B, 4=R, 5=Q, 6=K, 7=p, 8=n, 9=b, 10=r, 11=q, 12=k
    int init[64] = {
        4,2,3,5,6,3,2,4,
        1,1,1,1,1,1,1,1,
        0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,
        7,7,7,7,7,7,7,7,
        10,8,9,11,12,9,8,10
    };
    for (int i = 0; i < 64; ++i) board[i] = init[i];
}

bool MoonBotCpp::make_move(const Move& move) {
    // No legality check for brevity
    board[move.to] = board[move.from];
    board[move.from] = 0;
    white_to_move = !white_to_move;
    return true;
}

int MoonBotCpp::evaluate_board() const {
    int eval = 0;
    for (int i = 0; i < 64; ++i) {
        int p = board[i];
        switch (p) {
            case 1: eval += PAWN; break;
            case 2: eval += KNIGHT; break;
            case 3: eval += BISHOP; break;
            case 4: eval += ROOK; break;
            case 5: eval += QUEEN; break;
            case 6: eval += KING; break;
            case 7: eval -= PAWN; break;
            case 8: eval -= KNIGHT; break;
            case 9: eval -= BISHOP; break;
            case 10: eval -= ROOK; break;
            case 11: eval -= QUEEN; break;
            case 12: eval -= KING; break;
        }
    }
    return eval;
}

std::vector<Move> MoonBotCpp::generate_legal_moves() const {
    // Dummy: generate all single-square pawn pushes for the side to move
    std::vector<Move> moves;
    if (white_to_move) {
        for (int i = 8; i < 56; ++i) {
            if (board[i] == 1 && board[i+8] == 0) {
                moves.push_back({i, i+8, 0});
            }
        }
    } else {
        for (int i = 8; i < 56; ++i) {
            if (board[i] == 7 && board[i-8] == 0) {
                moves.push_back({i, i-8, 0});
            }
        }
    }
    return moves;
}

int MoonBotCpp::minimax(int depth, int alpha, int beta, bool maximizing, Move& best_move) {
    if (depth == 0) return evaluate_board();
    std::vector<Move> moves = generate_legal_moves();
    if (moves.empty()) return evaluate_board();
    int best_eval = maximizing ? -100000 : 100000;
    for (const auto& move : moves) {
        Board backup = board;
        bool old_turn = white_to_move;
        make_move(move);
        int eval = minimax(depth-1, alpha, beta, !maximizing, best_move);
        board = backup;
        white_to_move = old_turn;
        if (maximizing) {
            if (eval > best_eval) {
                best_eval = eval;
                best_move = move;
            }
            alpha = std::max(alpha, eval);
        } else {
            if (eval < best_eval) {
                best_eval = eval;
                best_move = move;
            }
            beta = std::min(beta, eval);
        }
        if (beta <= alpha) break;
    }
    return best_eval;
}

void MoonBotCpp::print_board() const {
    for (int r = 0; r < 8; ++r) {
        for (int c = 0; c < 8; ++c) {
            int p = board[r*8+c];
            std::cout << p << ' ';
        }
        std::cout << std::endl;
    }
}

// Example main
int main() {
    MoonBotCpp bot;
    bot.print_board();
    for (int i = 0; i < 10; ++i) {
        Move best_move;
        int eval = bot.minimax(2, -100000, 100000, bot.white_to_move, best_move);
        std::cout << "Best move: from " << best_move.from << " to " << best_move.to << ", eval: " << eval << std::endl;
        bot.make_move(best_move);
        bot.print_board();
    }
    return 0;
}
