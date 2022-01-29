#ifndef cantonese_lexer_h
#define cantonese_lexer_h

#include <cstdlib>
#include <deque>
#include <map>
#include "cantonese.hpp"
#define NEXT_CHAR mSource[mPosition + 1]

/// Current position
#define CURRENT_POS (&mSource[mPosition])
#define CURRENT_CHAR mSource[mPosition]
#define CURRENT_LINE mLine
#define CURRENT_TOKEN mCurrentToken

/// Set Current Token
#define TOKEN(K, S, len, line) { mCurrentToken.mType = K; \
mCurrentToken.mStart = S;  \
mCurrentToken.mLength = len; \
mCurrentToken.mLine = line; }

#define TOKEN_TYPE(K) mCurrentToken.mType = K;
#define TOKEN_LENGTH(l) {mCurrentToken.mLength = l;}
#define TOKEN_START mCurrentToken.mStart

// Get the next position
#define NEXT() {mPosition++;}

#define LEXER_UNKOWNCHAR(str) std::cout << "濑嘢 : Line " << mLine <<  "唔知" << str << "係咩? " <<std::endl

namespace cantonese {
    inline bool IsNumber(CAN_Char ch);
    inline bool IsAlpha(CAN_Char ch);
    inline bool IsCodeChar(CAN_Char ch);
    inline bool IsSpace(CAN_Char ch);

    enum class TokenType {
        End,
        Delimiter,
        Number,
        String,
        Identifier,
        Dot,
        Comma,
        LeftParen, // ( 
        RightParen,  // )
        LeftBracket, // [
        RightBracket, // ]
        LeftBrace,  // {
        RightBrace, // }

        //四则运算 + - * /
        Add,
        Sub,
        Mul,
        Div,

        Increase,  // ++
        Decrease, // --
        Assign, // assignment 赋值 =
        AddAssign, // += Addition assignment
        SubAssign, // -=Subtraction assignment and so on.....
        MulAssign,
        DivAssign,
        ModAssign,
        AndAssign,
        OrAssign,
        XorAssign,
        Arrow, //  ->

        //
        Not, // !
        Equal,  // ==
        NotEqual, // !=
        Greater, // >
        Less, // <
        GreaterEqual, // >=
        LessEqual, // <=

        // |
        Or,
        LogicOr,

        // &
        And,
        LogicAnd,

        // #
        Mod, // %

        At,  // @

        Colon,  // :

        KeywordIf,
        KeywordElse,
        KeywordPrint,
        KeywordPrintend,
        KeywordExit,
        KeywordIn,
        KeywordType,
        KeywordAssign,
        KeywordClassdef,
        KeywordIs,
        KeywordThen,
        KeywordDo,
        KeywordPass,
        KeywordWhileDo,
        KeywordFunction,
        KeywordCall,
        KeywordImport,
        KeywordFuncBegin,
        KeywordFuncEnd,
        KeywordAssert,
        KeywordClassAssign,
        KeywordWhile,
        KeywordWhileEnd,
        KeywordReturn,
        KeywordTry,
        KeywordExcept,
        KeywordFinally,
        KeywordRaise,
        KeywordRaiseEnd,
        KeywordFrom,
        KeywordTo,
        KeywordEndFor,
        KeywordExtend,
        KeywordMethed,
        KeywordEndClass,
        KeywordCmd,
        KeywordBreak,
        KeywordListAssign,
        KeywordSetAssign,
        KeywordGlobalSet,
        KeywordFalse,
        KeywordTrue,
        KeywordNone,
        KeywordStackinit,
        KeywordPush,
        KeywordPop,
        KeywordModel,
        KeywordModelNew,
        KeywordClassInit,
        KeywordSelf,
        KeywordCallBegin,
        KeywordDelete,
    };

    static std::map<String, TokenType> CANKeywords = {
         {_CAN_C("如果"),       TokenType::KeywordIf},
         {_CAN_C("唔系"),     TokenType::KeywordElse},
         {_CAN_C("畀我睇下"), TokenType::KeywordPrint},
         {_CAN_C("点样先"), TokenType::KeywordPrintend},
         {_CAN_C("收工"), TokenType::KeywordExit},
         {_CAN_C("喺"), TokenType::KeywordIn},
         {_CAN_C("起底"), TokenType::KeywordType},
         {_CAN_C("讲嘢"), TokenType::KeywordAssign},
         {_CAN_C("系"), TokenType::KeywordIs},
         {_CAN_C("嘅话"), TokenType::KeywordThen}
    };

    struct Token {
        TokenType mType{TokenType::End};
        const CAN_Char *mStart{};
        CAN_UINT32 mLength{};
        CAN_UINT32 mLine{};

        Token(TokenType mType, const CAN_Char *mStart, CAN_UINT32 mLength, CAN_UINT32 mLine);
        Token() = default;
        void dump(Ostream &os);
    };

    class Lexer {
    protected:
        bool mEof{false};
        std::deque<Token> mTokens;

        inline void GetNextToken();
        inline void SkipSpace();
        inline void SkipComment();
        inline void ParseIdentifier();
        inline void ParseString();
        inline void ParseNumber();

    public:
        Token mCurrentToken;

        Lexer(CAN_Char *mSource);
        ~Lexer();

        Token Read();
        TokenType ReadTokenType();
        TokenType PeekTokenType();
        void Consume();
        Token Peek(CAN_Integer i = 1);
        bool Match(TokenType tokenKind);

        CAN_Char *GetSource() {
            return mSource;
        }
    private:
        CAN_Char *mSource;
        CAN_UINT32 mPosition{0};
        CAN_UINT32 mLine{1};
    };
}

#endif /* cantonese_lexer_h */