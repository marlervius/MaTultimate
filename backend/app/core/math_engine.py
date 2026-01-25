import sympy as sp
from typing import Tuple, Optional

class MathEngine:
    """
    Kjerne-motor for matematisk verifisering og beregning ved bruk av SymPy.
    """
    def __init__(self):
        self.x = sp.symbols('x')

    def beregn_tangent(self, funksjon_str: str, x0: float) -> Tuple[str, float, float]:
        """
        Beregner tangentligningen y = ax + b for en gitt funksjon i et punkt x0.
        Returnerer (ligning_str, y0, stigningstall).
        """
        try:
            expr = sp.sympify(funksjon_str)
            y0 = float(expr.subs(self.x, x0))
            
            # Deriver funksjonen
            derivert = sp.diff(expr, self.x)
            stigningstall = float(derivert.subs(self.x, x0))
            
            # Tangentformel: y - y0 = f'(x0)(x - x0) => y = f'(x0)*x - f'(x0)*x0 + y0
            # y = ax + b der b = y0 - stigningstall * x0
            b = y0 - stigningstall * x0
            
            tangent_expr = f"{stigningstall}*x + ({b})"
            return tangent_expr, y0, stigningstall
            
        except Exception as e:
            raise ValueError(f"Kunne ikke beregne tangent for {funksjon_str}: {e}")

    def verify_derivative(self, funksjon_str: str, derivert_str: str) -> bool:
        """
        Verifiserer om derivert_str er den korrekte deriverte av funksjon_str.
        """
        try:
            expr = sp.sympify(funksjon_str)
            correct_derivert = sp.diff(expr, self.x)
            user_derivert = sp.sympify(derivert_str)
            
            # Sjekk om de er matematisk ekvivalente
            return sp.simplify(correct_derivert - user_derivert) == 0
        except Exception:
            return False
