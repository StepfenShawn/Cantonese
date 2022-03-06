#ifndef _AST_H_
#define _AST_H_

namespace {
    class ExprAST {
        public:
            virtual ~ExprAST() = default;
    };

    class NumberExprAST : public ExprAST {
        double Val;

        public:
            NumberExprAST(double Val) : Val(Val) {}
    };

}

#endif