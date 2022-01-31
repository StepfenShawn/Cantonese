#include <iostream>
#include "lexer.hpp"

namespace cantonese {

    bool IsSpace(CAN_Char ch){
        return ch == _CAN_C(' ') || ch == _CAN_C('\r');
    }
    bool IsNumber(CAN_Char ch) {
        return ch >= _CAN_C('0') && ch <= _CAN_C('9');
    }
    bool IsAlpha(CAN_Char ch) {
        return (ch >= _CAN_C('a') && ch <= _CAN_C('z')) || (ch >= _CAN_C('A') && ch <= _CAN_C('Z'));
    }
    bool IsCodeChar(CAN_Char ch) {
        return IsAlpha(ch) || ch == _CAN_C('_') || (ch >= _CAN_C('\u4e00') && ch <= _CAN_C('\u9fa5'));
    }
    
    void Token::dump(Ostream &os) {
        String name;
        switch (mType) {
            case TokenType::End:
                name = _CAN_C("<End>\n");
                break;
            case TokenType::Delimiter:
                name = _CAN_C("<newline>\n");
            case TokenType::Add:
                name = _CAN_C("+\n");
                break;
            case TokenType::Sub:
                name = _CAN_C("-\n");
                break;
            case TokenType::Mul:
                name = _CAN_C("*\n");
                break;
            case TokenType::Div:
                name = _CAN_C("/\n");
                break;
            case TokenType::Identifier:
            case TokenType::Number:
                name = String(mStart, mLength);
                break;
            case TokenType::String:
                break;
            case TokenType::Dot:
                name = _CAN_C(".\n");
                break;
            case TokenType::Comma:
                name = _CAN_C(",");
                break;
            case TokenType::LeftParen:
                name = _CAN_C("(\n");
                break;
            case TokenType::RightParen:
                name = _CAN_C(")\n");
                break;
            case TokenType::LeftBracket:
                name = _CAN_C("[\n");
                break;
            case TokenType::RightBracket:
                name = _CAN_C("]\n");
                break;
            case TokenType::LeftBrace:
                name = _CAN_C("{\n");
                break;
            case TokenType::RightBrace:
                name = _CAN_C("}\n");
                break;
            case TokenType::Increase:
                name = _CAN_C("++\n");
                break;
            case TokenType::Decrease:
                name = _CAN_C("--\n");
                break;
            case TokenType::Assign:
                name = _CAN_C("=\n");
                break;
            case TokenType::AddAssign:
                name = _CAN_C("+=\n");
                break;
            case TokenType::SubAssign:
                name = _CAN_C("-=\n");
                break;
            case TokenType::MulAssign:
                name = _CAN_C("*=\n");
                break;
            case TokenType::DivAssign:
                name = _CAN_C("/=\n");
                break;
            case TokenType::ModAssign:
                name = _CAN_C("%=\n");
                break;
            case TokenType::AndAssign:
                name = _CAN_C("&=\n");
                break;
            case TokenType::OrAssign:
                name = _CAN_C("|=\n");
                break;
            case TokenType::XorAssign:
                name = _CAN_C("^=\n");
                break;
            case TokenType::Arrow:
                name = _CAN_C("->\n");
                break;
            case TokenType::Not:
                name = _CAN_C("!\n");
                break;
            case TokenType::Equal:
                name = _CAN_C("==\n");
                break;
            case TokenType::NotEqual:
                name = _CAN_C("!=\n");
                break;
            case TokenType::Greater:
                name = _CAN_C(">\n");
                break;
            case TokenType::Less:
                name = _CAN_C("<\n");
                break;
            case TokenType::GreaterEqual:
                name = _CAN_C(">=\n");
                break;
            case TokenType::LessEqual:
                name = _CAN_C("<=\n");
                break;
            case TokenType::Or:
                name = _CAN_C("|\n");
                break;
            case TokenType::LogicOr:
                name = _CAN_C("||\n");
                break;
            case TokenType::And:
                name = _CAN_C("&\n");
                break;
            case TokenType::LogicAnd:
                name = _CAN_C("&&\n");
                break;
            case TokenType::Mod:
                name = _CAN_C("%\n");
                break;
            case TokenType::At:
                name = _CAN_C("@\n");
                break;
            case TokenType::Colon:
                name = _CAN_C(":\n");
                break;
            case TokenType::KeywordPrint:
                name = _CAN_C("KeywordPrint\n");
                break;
            case TokenType::KeywordPrintend:
                name = _CAN_C("KeywordPrintend\n");
                break;
            case TokenType::KeywordExit:
                name = _CAN_C("KeywordExit\n");
                break;
            case TokenType::KeywordAssign:
                name = _CAN_C("KeywordAssign\n");
                break;
            case TokenType::KeywordIs:
                name = _CAN_C("KeywordIs\n");
                break;
            default:
                name = _CAN_C("<unkown>\n");
        }
        os << name <<std::endl ;
    }

    // 读取一个Token
    void Lexer::GetNextToken() {
        if (mEof)
            return;
        // 跳过空格
        SkipSpace();
        switch (CURRENT_CHAR) {
            case _CAN_C('\n'):
                TOKEN(TokenType::Delimiter, CURRENT_POS, 1, CURRENT_LINE++);
                break;
            case _CAN_C(';'):
                TOKEN(TokenType::Delimiter, CURRENT_POS, 1, CURRENT_LINE); 
                break;
            case _CAN_C('('):
                TOKEN(TokenType::LeftParen, CURRENT_POS, 1, CURRENT_LINE);
                break;
            case _CAN_C(')'):
                TOKEN(TokenType::RightParen, CURRENT_POS, 1, CURRENT_LINE);
                break;
            case _CAN_C('['):
                TOKEN(TokenType::LeftBracket, CURRENT_POS, 1, CURRENT_LINE);
                break;
            case _CAN_C(']'):
                TOKEN(TokenType::RightBracket, CURRENT_POS, 1, CURRENT_LINE);
                break;
            case _CAN_C('{'):
                TOKEN(TokenType::LeftBrace, CURRENT_POS, 1, CURRENT_LINE);
                break;
            case _CAN_C('}'):
                TOKEN(TokenType::RightBrace, CURRENT_POS, 1, CURRENT_LINE);
                break;
            case _CAN_C('.'):
                TOKEN(TokenType::Dot, CURRENT_POS, 1, CURRENT_LINE);
                break;
            case _CAN_C('!'):
                if (NEXT_CHAR == _CAN_C('=')) {
                    TOKEN(TokenType::NotEqual, CURRENT_POS, 2, CURRENT_LINE);  // != not equal 不相等
                    NEXT();
                } else {
                    TOKEN(TokenType::Not, CURRENT_POS, 1, CURRENT_LINE);  // !
                }
                break;
            case _CAN_C('+'):
                if (NEXT_CHAR == _CAN_C('+')) {
                    TOKEN(TokenType::Increase, CURRENT_POS, 2, CURRENT_LINE); // ++
                    NEXT();
                } else if (NEXT_CHAR == _CAN_C('=')) {
                    TOKEN(TokenType::AddAssign, CURRENT_POS, 2, CURRENT_LINE); // +=
                    NEXT();
                } else {
                    TOKEN(TokenType::Add, CURRENT_POS, 1, CURRENT_LINE); // +
                }
                break;
            case _CAN_C('='):
                if (NEXT_CHAR == _CAN_C('=')) {
                    TOKEN(TokenType::Equal, CURRENT_POS, 2, CURRENT_LINE); // ==
                    NEXT();
                } else {
                    TOKEN(TokenType::Assign, CURRENT_POS, 1, CURRENT_LINE); // =
                }
                break;
            case _CAN_C('-'):
                if (NEXT_CHAR == _CAN_C('-')) { // --
                    TOKEN(TokenType::Decrease, CURRENT_POS, 1, CURRENT_LINE); // 自减
                    NEXT();
                } else if (NEXT_CHAR == _CAN_C('=')) { // -=
                    TOKEN(TokenType::SubAssign, CURRENT_POS, 1, CURRENT_LINE);
                    NEXT();
                } else if (NEXT_CHAR == _CAN_C('>')) { // -> Arrow 箭头
                    TOKEN(TokenType::Arrow, CURRENT_POS, 1, CURRENT_LINE);
                    NEXT();
                } else {
                    TOKEN(TokenType::Sub, CURRENT_POS, 1, CURRENT_LINE); // -
                }
                break;
            case _CAN_C('*'):
                TOKEN(TokenType::Mul, CURRENT_POS, 1, CURRENT_LINE);
                break;
            case _CAN_C(','):
                TOKEN(TokenType::Comma, CURRENT_POS, 1, CURRENT_LINE);
                break;
            
            case _CAN_C('/'):
                if (NEXT_CHAR == _CAN_C('/') || NEXT_CHAR == _CAN_C('*')) {
                    SkipComment();
                    return GetNextToken();
                } else {
                    TOKEN(TokenType::Div, CURRENT_POS, 1, CURRENT_LINE);
                }
                break;
            case _CAN_C('\0'):
                mEof = true;
                TOKEN(TokenType::End, CURRENT_POS, 0, CURRENT_LINE);
                return;
            default:
                if (IsCodeChar(CURRENT_CHAR)) {
                    ParseIdentifier();
                } else if (IsNumber(CURRENT_CHAR)) {
                    ParseNumber();
                } else if (CURRENT_CHAR == _CAN_C('"') || CURRENT_CHAR == _CAN_C('\'')) {
                    ParseString();
                } else {
                    //LEXER_UNKOWNCHAR(CURRENT_CHAR);
                    //wprintf(L"%S\n", &CURRENT_CHAR);
                    NEXT();
                }
                return;
        }
        NEXT();
    }

    void Lexer::SkipComment() {
        do {
            NEXT();
        } while (CURRENT_CHAR == _CAN_C('\n'));
        CURRENT_LINE++;
    }

    void Lexer::SkipSpace() {
        if (IsSpace(CURRENT_CHAR)){
            do {
                NEXT();
            } while (IsSpace(CURRENT_CHAR));
        }
    }

    bool Lexer::Match(TokenType tokenKind) {
        Token token = Peek(1);
        if (token.mType == tokenKind) {
            mTokens.pop_front();
            return true;
        }
        return false;
    }

    Token Lexer::Peek(CAN_Integer i) {
        while (mTokens.size() < i) {
            if (mEof)
                return CURRENT_TOKEN;
            GetNextToken();
            mTokens.push_back(CURRENT_TOKEN);
        }
        return mTokens[i - 1];
    }

    void Lexer::ParseNumber() {
        TOKEN(TokenType::Number, CURRENT_POS, 0, CURRENT_LINE);
        do {
            NEXT();
        } while (IsNumber(CURRENT_CHAR) || CURRENT_CHAR == _CAN_C('.'));
        TOKEN_LENGTH((CAN_UINT32)(CURRENT_POS - TOKEN_START));
    }
    void Lexer::ParseString() {
    
    }
    
    void Lexer::ParseIdentifier() {
        TOKEN(TokenType::Identifier, CURRENT_POS, 0, CURRENT_LINE);
        do {
            NEXT();
        } while (IsCodeChar(CURRENT_CHAR) || IsNumber(CURRENT_CHAR));
        TOKEN_LENGTH((CAN_UINT32)(CURRENT_POS - TOKEN_START));
        CAN_Char identifierBuffer[255] = {_CAN_C('\0')};
        memcpy(identifierBuffer, mCurrentToken.mStart, mCurrentToken.mLength * sizeof(CAN_Char));
        TokenType tok = CANKeywords[identifierBuffer];
        if (tok != TokenType::End) {
            TOKEN_TYPE(tok);
        }
    }

    Lexer::~Lexer() = default;

    Token Lexer::Read() {
        if (!mTokens.empty()) {
            Token token = mTokens.front();
            mTokens.pop_front();
            return token;
        }
        GetNextToken();
        return CURRENT_TOKEN;
    }

    Lexer::Lexer(CAN_Char *mSource) : mSource(mSource) {
    }

    TokenType Lexer::ReadTokenType() {
        GetNextToken();
        return CURRENT_TOKEN.mType;
    }

    TokenType Lexer::PeekTokenType() {
        if (mTokens.empty()) {
            GetNextToken();
            mTokens.push_back(mCurrentToken);
        }
        return mTokens[0].mType;
    }

    void Lexer::Consume() {
        if (!mTokens.empty())
            mTokens.pop_front();
        else
            GetNextToken();
    }

    Token::Token(TokenType mType, const CAN_Char *mStart, CAN_UINT32 mLength, CAN_UINT32 mLine) : mType(mType),
                                                                                            mStart(mStart),
                                                                                            mLength(mLength),
                                                                                            mLine(mLine) {
    }
}