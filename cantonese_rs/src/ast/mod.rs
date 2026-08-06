//! AST (Abstract Syntax Tree) definitions for the Cantonese language.
#![allow(dead_code)]

use crate::lexer::token::{Pos, Token};

/// Base marker for all expression nodes.
pub trait ExpNode {}

/// `null`
#[derive(Debug, Clone)]
pub struct NullExp;
impl ExpNode for NullExp {}

/// `True`
#[derive(Debug, Clone)]
pub struct TrueExp;
impl ExpNode for TrueExp {}

/// `False`
#[derive(Debug, Clone)]
pub struct FalseExp;
impl ExpNode for FalseExp {}

/// `<*>` (varargs)
#[derive(Debug, Clone)]
pub struct VarArgExp;
impl ExpNode for VarArgExp {}

/// Numeric literal.
#[derive(Debug, Clone)]
pub struct NumeralExp {
    pub val: String,
}
impl ExpNode for NumeralExp {}

/// `<->` string concatenation.
#[derive(Debug, Clone)]
pub struct ConcatExp {
    pub exps: Vec<Exp>,
}
impl ExpNode for ConcatExp {}

/// String literal.
#[derive(Debug, Clone)]
pub struct StringExp {
    pub s: String,
}
impl ExpNode for StringExp {}

/// List literal expression, e.g. `[a, b, c]`.
#[derive(Debug, Clone)]
pub struct ListExp {
    pub elem_exps: Vec<Exp>,
}
impl ExpNode for ListExp {}

/// Map/table literal expression, e.g. `{a, b, c}`.
#[derive(Debug, Clone)]
pub struct MapExp {
    pub elem_exps: Vec<Exp>,
}
impl ExpNode for MapExp {}

/// Unary operation expression, e.g. `-x` or `not x`.
#[derive(Debug, Clone)]
pub struct UnopExp {
    pub op: String,
    pub exp: Box<Exp>,
}
impl ExpNode for UnopExp {}

/// Binary operation expression, e.g. `a + b`.
#[derive(Debug, Clone)]
pub struct BinopExp {
    pub op: String,
    pub exp1: Box<Exp>,
    pub exp2: Box<Exp>,
}
impl ExpNode for BinopExp {}

/// Assignment expression, e.g. `a = b`.
#[derive(Debug, Clone)]
pub struct AssignExp {
    pub exp1: Box<Exp>,
    pub exp2: Box<Exp>,
}
impl ExpNode for AssignExp {}

/// Type annotation expression, e.g. `x: int`.
#[derive(Debug, Clone)]
pub struct AnnotationExp {
    pub exp: Box<Exp>,
    pub tyid: Box<Exp>,
}
impl ExpNode for AnnotationExp {}

/// Mapping expression, e.g. `a ==> b`.
#[derive(Debug, Clone)]
pub struct MappingExp {
    pub exp1: Box<Exp>,
    pub exp2: Box<Exp>,
}
impl ExpNode for MappingExp {}

/// Identifier expression.
#[derive(Debug, Clone)]
pub struct IdExp {
    pub name: String,
}
impl ExpNode for IdExp {}

/// Parenthesised expression: `(exp)`.
#[derive(Debug, Clone)]
pub struct ParensExp {
    pub exp: Box<Exp>,
}
impl ExpNode for ParensExp {}

/// Object/attribute access expression, e.g. `obj->field` or `obj. field`.
#[derive(Debug, Clone)]
pub struct ObjectAccessExp {
    pub prefix_exp: Box<Exp>,
    pub key_exp: Box<Exp>,
}
impl ExpNode for ObjectAccessExp {}

/// List/array access expression, e.g. `xs[i]`.
#[derive(Debug, Clone)]
pub struct ListAccessExp {
    pub prefix_exp: Box<Exp>,
    pub key_exp: Box<Exp>,
}
impl ExpNode for ListAccessExp {}

/// Attribute access expression used as a suffix.
#[derive(Debug, Clone)]
pub struct AttrAccessExp {
    pub key_exp: Box<Exp>,
}
impl ExpNode for AttrAccessExp {}

/// Function call expression.
#[derive(Debug, Clone)]
pub struct FuncCallExp {
    pub prefix_exp: Box<Exp>,
    pub args: Vec<Exp>,
}
impl ExpNode for FuncCallExp {}

/// Lambda/anonymous function expression.
#[derive(Debug, Clone)]
pub struct LambdaExp {
    pub id_list: Vec<Exp>,
    pub blocks: Vec<Exp>,
}
impl ExpNode for LambdaExp {}

/// If-else expression.
#[derive(Debug, Clone)]
pub struct IfElseExp {
    pub if_cond_exp: Box<Exp>,
    pub if_exp: Box<Exp>,
    pub else_exp: Box<Exp>,
}
impl ExpNode for IfElseExp {}

/// Qualified/nested names expression.
#[derive(Debug, Clone)]
pub struct NamesExp {
    pub child: Vec<Exp>,
}
impl ExpNode for NamesExp {}

/// Meta variable appearing inside macro *blocks* (output side), e.g. `@v`.
/// Defined before the `Exp` enum so it can be included as a variant.
#[derive(Debug, Clone)]
pub struct MetaIdExp {
    pub name: String,
}
impl ExpNode for MetaIdExp {}

/// Union of all expression nodes.
#[derive(Debug, Clone)]
pub enum Exp {
    Null(NullExp),
    True(TrueExp),
    False(FalseExp),
    VarArg(VarArgExp),
    Numeral(NumeralExp),
    Concat(ConcatExp),
    String(StringExp),
    List(ListExp),
    Map(MapExp),
    Unop(UnopExp),
    Binop(BinopExp),
    Assign(AssignExp),
    Annotation(AnnotationExp),
    Mapping(MappingExp),
    Id(IdExp),
    Parens(ParensExp),
    ObjectAccess(ObjectAccessExp),
    ListAccess(ListAccessExp),
    AttrAccess(AttrAccessExp),
    FuncCall(FuncCallExp),
    Lambda(LambdaExp),
    IfElse(IfElseExp),
    Names(NamesExp),
    MetaId(MetaIdExp),
    PatRep(Box<MacroMetaRepExpInPat>),
    BlockRep(Box<MacroMetaRepExpInBlock>),
    /// Result of expanding a statement-level macro inside an expression parse.
    /// Used to bridge the strongly-typed `Exp`/`Stat` split back to `StatParser`.
    StatExpansion(Box<Stat>),
}

impl ExpNode for Exp {}

/// Base marker for all statement nodes.
pub trait StatNode {}

/// Function call statement.
#[derive(Debug, Clone)]
pub struct FuncCallStat {
    pub func_name: Exp,
    pub args: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for FuncCallStat {}

/// If statement with optional elif/else branches.
#[derive(Debug, Clone)]
pub struct IfStat {
    pub if_exp: Exp,
    pub if_block: Vec<Stat>,
    pub elif_exps: Vec<Exp>,
    pub elif_blocks: Vec<Vec<Stat>>,
    pub else_blocks: Vec<Vec<Stat>>,
    pub pos: Option<Pos>,
}
impl StatNode for IfStat {}

/// Print statement.
#[derive(Debug, Clone)]
pub struct PrintStat {
    pub args: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for PrintStat {}

/// Pass statement.
#[derive(Debug, Clone)]
pub struct PassStat {
    pub pos: Option<Pos>,
}
impl StatNode for PassStat {}

/// Assignment statement.
#[derive(Debug, Clone)]
pub struct AssignStat {
    pub var_list: Vec<Exp>,
    pub exp_list: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for AssignStat {}

/// Multi-variable block assignment statement.
#[derive(Debug, Clone)]
pub struct AssignBlockStat {
    pub var_list: Vec<Exp>,
    pub exp_list: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for AssignBlockStat {}

/// Numeric for-loop statement.
#[derive(Debug, Clone)]
pub struct ForStat {
    pub var: Exp,
    pub from_exp: Exp,
    pub to_exp: Exp,
    pub blocks: Vec<Stat>,
    pub pos: Option<Pos>,
}
impl StatNode for ForStat {}

/// Iterator for-each statement.
#[derive(Debug, Clone)]
pub struct ForEachStat {
    pub id_list: Vec<Exp>,
    pub exp_list: Vec<Exp>,
    pub blocks: Vec<Stat>,
    pub pos: Option<Pos>,
}
impl StatNode for ForEachStat {}

/// While-loop statement.
#[derive(Debug, Clone)]
pub struct WhileStat {
    pub cond_exp: Exp,
    pub blocks: Vec<Stat>,
    pub pos: Option<Pos>,
}
impl StatNode for WhileStat {}

/// List initialisation statement.
#[derive(Debug, Clone)]
pub struct ListInitStat {
    pub pos: Option<Pos>,
}
impl StatNode for ListInitStat {}

/// Function definition statement.
#[derive(Debug, Clone)]
pub struct FunctionDefStat {
    pub name_exp: Exp,
    pub args: Vec<Exp>,
    pub blocks: Vec<Stat>,
    pub pos: Option<Pos>,
}
impl StatNode for FunctionDefStat {}

/// Function type signature definition statement.
#[derive(Debug, Clone)]
pub struct FuncTypeDefStat {
    pub func_name: Exp,
    pub args_type: Vec<Exp>,
    pub return_type: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for FuncTypeDefStat {}

/// Method definition statement.
#[derive(Debug, Clone)]
pub struct MethodDefStat {
    pub name_exp: Exp,
    pub args: Vec<Exp>,
    pub class_blocks: Vec<Stat>,
    pub pos: Option<Pos>,
}
impl StatNode for MethodDefStat {}

/// Attribute definition statement.
#[derive(Debug, Clone)]
pub struct AttrDefStat {
    pub attrs_list: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for AttrDefStat {}

/// Class definition statement.
#[derive(Debug, Clone)]
pub struct ClassDefStat {
    pub class_name: Exp,
    pub class_extend: Vec<Exp>,
    pub class_blocks: Vec<Stat>,
    pub pos: Option<Pos>,
}
impl StatNode for ClassDefStat {}

/// Import statement.
#[derive(Debug, Clone)]
pub struct ImportStat {
    pub names: Exp,
    pub pos: Option<Pos>,
}
impl StatNode for ImportStat {}

/// Raise/throw statement.
#[derive(Debug, Clone)]
pub struct RaiseStat {
    pub name_exp: Exp,
    pub pos: Option<Pos>,
}
impl StatNode for RaiseStat {}

/// Try-except-finally statement.
#[derive(Debug, Clone)]
pub struct TryStat {
    pub try_blocks: Vec<Stat>,
    pub except_exps: Vec<Exp>,
    pub except_blocks: Vec<Vec<Stat>>,
    pub finally_blocks: Vec<Stat>,
    pub pos: Option<Pos>,
}
impl StatNode for TryStat {}

/// Global declaration statement.
#[derive(Debug, Clone)]
pub struct GlobalStat {
    pub idlist: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for GlobalStat {}

/// Break statement.
#[derive(Debug, Clone)]
pub struct BreakStat {
    pub pos: Option<Pos>,
}
impl StatNode for BreakStat {}

/// Continue statement.
#[derive(Debug, Clone)]
pub struct ContinueStat {
    pub pos: Option<Pos>,
}
impl StatNode for ContinueStat {}

/// Type declaration statement.
#[derive(Debug, Clone)]
pub struct TypeStat {
    pub exps: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for TypeStat {}

/// Assert statement.
#[derive(Debug, Clone)]
pub struct AssertStat {
    pub exps: Exp,
    pub pos: Option<Pos>,
}
impl StatNode for AssertStat {}

/// Return statement.
#[derive(Debug, Clone)]
pub struct ReturnStat {
    pub exps: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for ReturnStat {}

/// Delete statement.
#[derive(Debug, Clone)]
pub struct DelStat {
    pub exps: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for DelStat {}

/// Shell/command statement.
#[derive(Debug, Clone)]
pub struct CmdStat {
    pub args: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for CmdStat {}

/// Method call statement.
#[derive(Debug, Clone)]
pub struct MethodCallStat {
    pub name_exp: Exp,
    pub method: Exp,
    pub args: Vec<Exp>,
    pub pos: Option<Pos>,
}
impl StatNode for MethodCallStat {}

/// Expression statement (a bare expression).
#[derive(Debug, Clone)]
pub struct CallStat {
    pub exp: Exp,
    pub pos: Option<Pos>,
}
impl StatNode for CallStat {}

/// Pattern-match statement.
#[derive(Debug, Clone)]
pub struct MatchStat {
    pub match_id: Exp,
    pub match_val: Vec<Exp>,
    pub match_block: Vec<Vec<Stat>>,
    pub default_match_block: Vec<Stat>,
    pub pos: Option<Pos>,
}
impl StatNode for MatchStat {}

/// Inline native-code extension statement.
#[derive(Debug, Clone)]
pub struct ExtendStat {
    pub code: String,
    pub pos: Option<Pos>,
}
impl StatNode for ExtendStat {}

/// Exit statement.
#[derive(Debug, Clone)]
pub struct ExitStat {
    pub pos: Option<Pos>,
}
impl StatNode for ExitStat {}

/// Macro definition statement.
/// Defined before the `Stat` enum so it can be included as a variant.
#[derive(Debug, Clone)]
pub struct MacroDefStat {
    pub match_pats: Vec<Vec<MacroPatItem>>,
    pub match_block: Vec<TokenTree>,
    pub pos: Option<Pos>,
}
impl StatNode for MacroDefStat {}

/// Union of all statement nodes.
#[derive(Debug, Clone)]
pub enum Stat {
    FuncCall(FuncCallStat),
    If(IfStat),
    Print(PrintStat),
    Pass(PassStat),
    Assign(AssignStat),
    AssignBlock(AssignBlockStat),
    For(ForStat),
    ForEach(ForEachStat),
    While(WhileStat),
    ListInit(ListInitStat),
    FunctionDef(FunctionDefStat),
    FuncTypeDef(FuncTypeDefStat),
    MethodDef(MethodDefStat),
    AttrDef(AttrDefStat),
    ClassDef(ClassDefStat),
    Import(ImportStat),
    Raise(RaiseStat),
    Try(TryStat),
    Global(GlobalStat),
    Break(BreakStat),
    Continue(ContinueStat),
    Type(TypeStat),
    Assert(AssertStat),
    Return(ReturnStat),
    Del(DelStat),
    Cmd(CmdStat),
    MethodCall(MethodCallStat),
    Call(CallStat),
    Match(MatchStat),
    Extend(ExtendStat),
    Exit(ExitStat),
    MacroDef(MacroDefStat),
}

impl StatNode for Stat {}

// =============================================================================
// Macro nodes
// =============================================================================

/// Meta id inside macro *patterns* (input side), e.g. `@v: str`.
#[derive(Debug, Clone)]
pub struct MacroMetaId {
    pub id: Exp,
    pub frag_spec: Exp,
}

/// A single item that can appear inside a macro pattern's repetition group.
#[derive(Debug, Clone)]
pub enum MacroPatItem {
    Token(Token),
    MetaVar(MacroMetaId),
    MetaId(MetaIdExp),
    Rep(Box<MacroMetaRepExpInPat>),
    Tree(TokenTree),
}

/// Meta expression inside macro *patterns* (input), e.g. `$(...)+`.
#[derive(Debug, Clone)]
pub struct MacroMetaRepExpInPat {
    pub token_trees: Vec<MacroPatItem>,
    pub rep_sep: Option<Token>,
    pub rep_op: String,
}

/// A single item that can appear inside a macro body's token tree.
#[derive(Debug, Clone)]
pub enum MacroBodyItem {
    Token(Token),
    MetaId(MetaIdExp),
    Rep(Box<MacroMetaRepExpInBlock>),
    Tree(TokenTree),
}

/// Meta expression inside macro *blocks* (output), e.g. `${...}+`.
#[derive(Debug, Clone)]
pub struct MacroMetaRepExpInBlock {
    pub token_trees: TokenTree,
    pub rep_sep: Option<Exp>,
    pub rep_op: Option<Exp>,
}

/// A child element of a [`TokenTree`].
#[derive(Debug, Clone)]
pub enum TokenTreeChild {
    Token(Token),
    MetaId(MetaIdExp),
    MacroCall(CallMacro),
    PatRep(Box<MacroMetaRepExpInPat>),
    BlockRep(Box<MacroMetaRepExpInBlock>),
    Tree(TokenTree),
}

/// A balanced delimited group of tokens used by the macro system.
#[derive(Debug, Clone)]
pub struct TokenTree {
    pub child: Vec<TokenTreeChild>,
    pub open_ch: Token,
    pub close_ch: Token,
}

/// A macro invocation.
#[derive(Debug, Clone)]
pub struct CallMacro {
    pub name: String,
    pub token_trees: Vec<TokenTreeChild>,
}

/// Top-level AST union
#[derive(Debug, Clone)]
pub enum Ast {
    Stat(Stat),
    Exp(Exp),
    TokenTree(TokenTree),
}
