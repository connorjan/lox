import Expr
import Stmt

class LoxPass:
    """
    Bass class for lox passes
    """

    def __init__(self, pure: bool = True):
        """
        If pure is left undeclared or set to True, the derived class must
        implement all of the methods
        """
        self.pure = pure

    def isPure(self) -> bool:
        """ Returns True if pure is not an attribute or set to False """
        return not hasattr(self, "pure") or self.pure

    # Visitor methods
    def visitBlockStmt(self, stmt: Stmt.Block) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitBreakStmt(self, stmt: Stmt.Break) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitContinueStmt(self, stmt: Stmt.Continue) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitExpressionStmt(self, stmt: Stmt.Expression) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitFunctionStmt(self, stmt: Stmt.Function) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitIfStmt(self, stmt: Stmt.If) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitReturnStmt(self, stmt: Stmt.Return) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitWhileStmt(self, stmt: Stmt.While) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitVarStmt(self, stmt: Stmt.Var) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitAssignExpr(self, expr: Expr.Assign) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitBinaryExpr(self, expr: Expr.Binary) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitCallExpr(self, expr: Expr.Call) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitGroupingExpr(self, expr: Expr.Grouping) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitLiteralExpr(self, expr: Expr.Literal) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitLogicalExpr(self, expr: Expr.Logical) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitUnaryExpr(self, expr: Expr.Unary) -> None:
        if self.isPure():
            raise NotImplementedError

    def visitVariableExpr(self, expr: Expr.Variable) -> None:
        if self.isPure():
            raise NotImplementedError
