"""
MaTultimate Math Engine
========================
SymPy-basert matematisk verifisering og generering.
Dette er sannhetskilden - LLM-er foreslår, SymPy bekrefter.

Forfatter: Marius Lervik
"""

from typing import Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import random
import re

from sympy import (
    symbols, Symbol, 
    diff, integrate, limit, solve, simplify, expand, factor,
    sin, cos, tan, ln, log, exp, sqrt, Abs,
    oo, pi, E,
    Rational, Integer,
    latex as sympy_latex,
    parse_expr,
    Eq, Lt, Le, Gt, Ge,
    Derivative, Integral,
    sympify,
    N  # For numerisk evaluering
)
from sympy.parsing.latex import parse_latex
from sympy.core.sympify import SympifyError


class MathError(Exception):
    """Baseklasse for matematikkfeil."""
    pass


class VerificationError(MathError):
    """Feil ved verifisering av matematisk uttrykk."""
    pass


class ParseError(MathError):
    """Feil ved parsing av matematisk uttrykk."""
    pass


class OperationType(str, Enum):
    """Typer matematiske operasjoner."""
    DERIVATIVE = "derivative"
    INTEGRAL_INDEFINITE = "integral_indefinite"
    INTEGRAL_DEFINITE = "integral_definite"
    EQUATION = "equation"
    SIMPLIFY = "simplify"
    FACTOR = "factor"
    EXPAND = "expand"
    LIMIT = "limit"


@dataclass
class VerificationResult:
    """Resultat av en matematisk verifisering."""
    is_correct: bool
    expected: str  # LaTeX-format
    got: str  # LaTeX-format
    simplified_difference: Optional[str] = None
    message: str = ""


@dataclass
class Step:
    """Ett steg i en steg-for-steg løsning."""
    description: str  # Norsk beskrivelse
    expression: str  # LaTeX-format
    rule_applied: Optional[str] = None  # F.eks. "Produktregelen"


@dataclass
class StepByStepSolution:
    """Komplett steg-for-steg løsning."""
    problem: str  # LaTeX
    steps: list[Step]
    final_answer: str  # LaTeX
    verification: VerificationResult


@dataclass
class ProblemVariant:
    """En variant av et problem med garantert korrekt svar."""
    problem_latex: str
    answer_latex: str
    difficulty: float  # 0.0 - 1.0
    parameters: dict = field(default_factory=dict)


class MathEngine:
    """
    Hovedklasse for matematisk verifisering og generering.
    
    Eksempel:
        engine = MathEngine()
        result = engine.verify_derivative("x**2", "2*x")
        assert result.is_correct
    """
    
    def __init__(self):
        # Standard symboler
        self.x = symbols('x')
        self.y = symbols('y')
        self.t = symbols('t')
        self.n = symbols('n', integer=True)
        
        # Vanlige symboler for VGS
        self.common_symbols = {
            'x': self.x,
            'y': self.y,
            't': self.t,
            'n': self.n,
            'pi': pi,
            'e': E,
        }
    
    def parse_expression(self, expr_str: str, from_latex: bool = False) -> Symbol:
        """
        Parse et matematisk uttrykk til SymPy.
        
        Args:
            expr_str: Uttrykket som streng (Python-syntaks eller LaTeX)
            from_latex: Om inputen er LaTeX
            
        Returns:
            SymPy-uttrykk
            
        Raises:
            ParseError: Ved ugyldig syntaks
        """
        try:
            if from_latex:
                # Rens LaTeX først
                expr_str = self._clean_latex(expr_str)
                return parse_latex(expr_str)
            else:
                # Python-syntaks
                return parse_expr(expr_str, local_dict=self.common_symbols)
        except (SympifyError, Exception) as e:
            raise ParseError(f"Kunne ikke parse uttrykket '{expr_str}': {e}")
    
    def _clean_latex(self, latex_str: str) -> str:
        """Rens LaTeX-streng for parsing."""
        # Fjern $ tegn
        latex_str = latex_str.replace('$', '')
        # Fjern \displaystyle etc.
        latex_str = re.sub(r'\\displaystyle\s*', '', latex_str)
        # Standardiser brøk
        latex_str = latex_str.replace('\\dfrac', '\\frac')
        return latex_str.strip()
    
    def to_latex(self, expr) -> str:
        """Konverter SymPy-uttrykk til LaTeX."""
        return sympy_latex(expr)
    
    # =========================================================================
    # VERIFISERING
    # =========================================================================
    
    def verify_derivative(
        self, 
        f: str, 
        f_prime: str, 
        variable: str = 'x',
        from_latex: bool = False
    ) -> VerificationResult:
        """
        Verifiser at f'(x) er korrekt derivert.
        
        Args:
            f: Funksjonen f(x)
            f_prime: Den oppgitte deriverte f'(x)
            variable: Variabelen det deriveres med hensyn på
            from_latex: Om input er LaTeX
            
        Returns:
            VerificationResult med is_correct=True/False
            
        Eksempel:
            >>> engine.verify_derivative("x**3", "3*x**2")
            VerificationResult(is_correct=True, ...)
        """
        try:
            var = symbols(variable)
            f_expr = self.parse_expression(f, from_latex)
            f_prime_expr = self.parse_expression(f_prime, from_latex)
            
            # Beregn korrekt derivert
            correct_derivative = diff(f_expr, var)
            
            # Sammenlign ved å forenkle differansen
            difference = simplify(correct_derivative - f_prime_expr)
            is_correct = difference == 0
            
            return VerificationResult(
                is_correct=is_correct,
                expected=self.to_latex(correct_derivative),
                got=self.to_latex(f_prime_expr),
                simplified_difference=self.to_latex(difference) if not is_correct else None,
                message="Korrekt!" if is_correct else f"Forventet {self.to_latex(correct_derivative)}"
            )
        except ParseError as e:
            return VerificationResult(
                is_correct=False,
                expected="",
                got="",
                message=str(e)
            )
    
    def verify_integral(
        self,
        f: str,
        F: str,
        variable: str = 'x',
        lower_bound: Optional[str] = None,
        upper_bound: Optional[str] = None,
        from_latex: bool = False
    ) -> VerificationResult:
        """
        Verifiser at F(x) er korrekt integral av f(x).
        
        For ubestemt integral: Sjekker at F'(x) = f(x)
        For bestemt integral: Beregner verdien og sammenligner
        """
        try:
            var = symbols(variable)
            f_expr = self.parse_expression(f, from_latex)
            F_expr = self.parse_expression(F, from_latex)
            
            if lower_bound is not None and upper_bound is not None:
                # Bestemt integral
                lower = self.parse_expression(lower_bound, from_latex)
                upper = self.parse_expression(upper_bound, from_latex)
                
                correct_value = integrate(f_expr, (var, lower, upper))
                difference = simplify(correct_value - F_expr)
                is_correct = difference == 0
                
                return VerificationResult(
                    is_correct=is_correct,
                    expected=self.to_latex(correct_value),
                    got=self.to_latex(F_expr),
                    simplified_difference=self.to_latex(difference) if not is_correct else None,
                    message="Korrekt!" if is_correct else f"Forventet {self.to_latex(correct_value)}"
                )
            else:
                # Ubestemt integral - sjekk at F'(x) = f(x)
                F_derivative = diff(F_expr, var)
                difference = simplify(F_derivative - f_expr)
                is_correct = difference == 0
                
                # Beregn også "standard" antiderivert for sammenligning
                correct_integral = integrate(f_expr, var)
                
                return VerificationResult(
                    is_correct=is_correct,
                    expected=self.to_latex(correct_integral) + " + C",
                    got=self.to_latex(F_expr),
                    simplified_difference=self.to_latex(difference) if not is_correct else None,
                    message="Korrekt!" if is_correct else f"F'(x) = {self.to_latex(F_derivative)}, men f(x) = {self.to_latex(f_expr)}"
                )
        except ParseError as e:
            return VerificationResult(
                is_correct=False,
                expected="",
                got="",
                message=str(e)
            )
    
    def verify_equation_solution(
        self,
        equation: str,
        solution: str,
        variable: str = 'x',
        from_latex: bool = False
    ) -> VerificationResult:
        """
        Verifiser at en likning er løst korrekt.
        
        Args:
            equation: Likningen (f.eks. "x**2 - 4 = 0" eller "x**2 - 4")
            solution: Den oppgitte løsningen (f.eks. "2" eller "-2, 2")
            
        Eksempel:
            >>> engine.verify_equation_solution("x**2 - 4", "2")  # Delvis korrekt
            >>> engine.verify_equation_solution("x**2 - 4", "-2, 2")  # Helt korrekt
        """
        try:
            var = symbols(variable)
            
            # Parse likningen
            if '=' in equation:
                left, right = equation.split('=')
                eq_expr = self.parse_expression(left, from_latex) - self.parse_expression(right, from_latex)
            else:
                eq_expr = self.parse_expression(equation, from_latex)
            
            # Finn korrekte løsninger
            correct_solutions = solve(eq_expr, var)
            
            # Parse oppgitte løsninger
            solution_strs = [s.strip() for s in solution.replace(' ', '').split(',')]
            given_solutions = [self.parse_expression(s, from_latex) for s in solution_strs]
            
            # Sammenlign (som sett, rekkefølge spiller ingen rolle)
            correct_set = set(correct_solutions)
            given_set = set(given_solutions)
            
            is_correct = correct_set == given_set
            
            return VerificationResult(
                is_correct=is_correct,
                expected=", ".join(self.to_latex(s) for s in correct_solutions),
                got=", ".join(self.to_latex(s) for s in given_solutions),
                message="Korrekt!" if is_correct else f"Mangler løsninger eller feil løsninger"
            )
        except ParseError as e:
            return VerificationResult(
                is_correct=False,
                expected="",
                got="",
                message=str(e)
            )
    
    def verify_simplification(
        self,
        original: str,
        simplified: str,
        from_latex: bool = False
    ) -> VerificationResult:
        """Verifiser at to uttrykk er algebraisk like."""
        try:
            orig_expr = self.parse_expression(original, from_latex)
            simp_expr = self.parse_expression(simplified, from_latex)
            
            difference = simplify(orig_expr - simp_expr)
            is_correct = difference == 0
            
            return VerificationResult(
                is_correct=is_correct,
                expected=self.to_latex(simplify(orig_expr)),
                got=self.to_latex(simp_expr),
                simplified_difference=self.to_latex(difference) if not is_correct else None,
                message="Uttrykkene er like!" if is_correct else "Uttrykkene er ikke algebraisk like"
            )
        except ParseError as e:
            return VerificationResult(
                is_correct=False,
                expected="",
                got="",
                message=str(e)
            )
    
    # =========================================================================
    # BEREGNING
    # =========================================================================
    
    def compute_derivative(
        self,
        f: str,
        variable: str = 'x',
        order: int = 1,
        from_latex: bool = False
    ) -> str:
        """
        Beregn den deriverte av f.
        
        Args:
            f: Funksjonen
            variable: Variabel
            order: Orden (1 = første deriverte, 2 = andre, osv.)
            
        Returns:
            LaTeX-streng av den deriverte
        """
        var = symbols(variable)
        f_expr = self.parse_expression(f, from_latex)
        
        result = f_expr
        for _ in range(order):
            result = diff(result, var)
        
        return self.to_latex(simplify(result))
    
    def compute_integral(
        self,
        f: str,
        variable: str = 'x',
        lower_bound: Optional[str] = None,
        upper_bound: Optional[str] = None,
        from_latex: bool = False
    ) -> str:
        """Beregn integralet av f."""
        var = symbols(variable)
        f_expr = self.parse_expression(f, from_latex)
        
        if lower_bound is not None and upper_bound is not None:
            lower = self.parse_expression(lower_bound, from_latex)
            upper = self.parse_expression(upper_bound, from_latex)
            result = integrate(f_expr, (var, lower, upper))
        else:
            result = integrate(f_expr, var)
        
        latex_result = self.to_latex(simplify(result))
        
        # Legg til + C for ubestemte integraler
        if lower_bound is None:
            latex_result += " + C"
        
        return latex_result
    
    def solve_equation(
        self,
        equation: str,
        variable: str = 'x',
        from_latex: bool = False
    ) -> list[str]:
        """Løs en likning og returner løsningene som LaTeX."""
        var = symbols(variable)
        
        if '=' in equation:
            left, right = equation.split('=')
            eq_expr = self.parse_expression(left, from_latex) - self.parse_expression(right, from_latex)
        else:
            eq_expr = self.parse_expression(equation, from_latex)
        
        solutions = solve(eq_expr, var)
        return [self.to_latex(s) for s in solutions]
    
    def find_extrema(
        self,
        f: str,
        variable: str = 'x',
        from_latex: bool = False
    ) -> dict:
        """
        Finn ekstremalpunkter for en funksjon.
        
        Returns:
            {
                'critical_points': [...],  # x-verdier
                'second_derivative_test': [
                    {'x': ..., 'type': 'minimum'|'maximum'|'inflection', 'y': ...}
                ]
            }
        """
        var = symbols(variable)
        f_expr = self.parse_expression(f, from_latex)
        
        # Finn kritiske punkter (f'(x) = 0)
        f_prime = diff(f_expr, var)
        critical_points = solve(f_prime, var)
        
        # Andre deriverte for klassifisering
        f_double_prime = diff(f_prime, var)
        
        results = []
        for cp in critical_points:
            # Evaluer f''(cp)
            second_deriv_value = f_double_prime.subs(var, cp)
            y_value = f_expr.subs(var, cp)
            
            if second_deriv_value > 0:
                point_type = "minimum"
            elif second_deriv_value < 0:
                point_type = "maximum"
            else:
                point_type = "vendepunkt_eller_ukjent"
            
            results.append({
                'x': self.to_latex(cp),
                'y': self.to_latex(simplify(y_value)),
                'type': point_type,
                'f_double_prime': self.to_latex(second_deriv_value)
            })
        
        return {
            'critical_points': [self.to_latex(cp) for cp in critical_points],
            'analysis': results,
            'f_prime': self.to_latex(f_prime),
            'f_double_prime': self.to_latex(f_double_prime)
        }
    
    # =========================================================================
    # STEG-FOR-STEG LØSNINGER
    # =========================================================================
    
    def derivative_step_by_step(
        self,
        f: str,
        variable: str = 'x',
        from_latex: bool = False
    ) -> StepByStepSolution:
        """
        Generer steg-for-steg løsning for derivasjon.
        
        Identifiserer hvilke regler som brukes og viser mellomsteg.
        """
        var = symbols(variable)
        f_expr = self.parse_expression(f, from_latex)
        
        steps = []
        
        # Steg 1: Vis oppgaven
        steps.append(Step(
            description="Vi skal derivere funksjonen:",
            expression=f"f({variable}) = {self.to_latex(f_expr)}"
        ))
        
        # Identifiser type funksjon og velg strategi
        steps.extend(self._identify_derivative_strategy(f_expr, var))
        
        # Beregn svaret
        result = diff(f_expr, var)
        simplified_result = simplify(result)
        
        # Siste steg: Svaret
        steps.append(Step(
            description="Svaret blir:",
            expression=f"f'({variable}) = {self.to_latex(simplified_result)}"
        ))
        
        # Verifiser
        verification = self.verify_derivative(f, self.to_latex(simplified_result), variable)
        
        return StepByStepSolution(
            problem=f"f({variable}) = {self.to_latex(f_expr)}",
            steps=steps,
            final_answer=self.to_latex(simplified_result),
            verification=verification
        )
    
    def _identify_derivative_strategy(self, expr, var) -> list[Step]:
        """Identifiser hvilke derivasjonsregler som trengs."""
        steps = []
        
        # Sjekk for produkt
        if expr.is_Mul and len(expr.args) > 1:
            # Sjekk om det er mer enn bare en konstant ganger noe
            non_const = [a for a in expr.args if a.has(var)]
            if len(non_const) > 1:
                steps.append(Step(
                    description="Dette er et produkt av to funksjoner, så vi bruker produktregelen:",
                    expression=r"(u \cdot v)' = u' \cdot v + u \cdot v'",
                    rule_applied="Produktregelen"
                ))
        
        # Sjekk for brøk
        elif expr.is_Pow and expr.args[1] == -1:
            steps.append(Step(
                description="Dette er en brøk, så vi bruker brøkregelen:",
                expression=r"\left(\frac{u}{v}\right)' = \frac{u' \cdot v - u \cdot v'}{v^2}",
                rule_applied="Brøkregelen"
            ))
        
        # Sjekk for sammensetning (kjerneregel)
        elif expr.is_Function or (expr.is_Pow and expr.args[1].has(var)):
            inner = None
            if expr.is_Function and expr.args[0] != var:
                inner = expr.args[0]
            elif expr.is_Pow and expr.args[0].has(var) and expr.args[0] != var:
                inner = expr.args[0]
            
            if inner and inner != var:
                steps.append(Step(
                    description="Dette er en sammensatt funksjon, så vi bruker kjerneregelen:",
                    expression=r"(f(g(x)))' = f'(g(x)) \cdot g'(x)",
                    rule_applied="Kjerneregelen"
                ))
                steps.append(Step(
                    description=f"Den indre funksjonen er:",
                    expression=f"g({var}) = {self.to_latex(inner)}"
                ))
        
        # Enkel potensregel
        elif expr.is_Pow and expr.args[1].is_number:
            n = expr.args[1]
            steps.append(Step(
                description="Vi bruker potensregelen:",
                expression=r"(x^n)' = n \cdot x^{n-1}",
                rule_applied="Potensregelen"
            ))
        
        # Sum/differanse
        elif expr.is_Add:
            steps.append(Step(
                description="Vi deriverer ledd for ledd:",
                expression=r"(f + g)' = f' + g'",
                rule_applied="Sumregelen"
            ))
        
        return steps
    
    # =========================================================================
    # VARIANT-GENERERING
    # =========================================================================
    
    def generate_derivative_variants(
        self,
        template: str,
        num_variants: int = 5,
        difficulty: float = 0.5,
        param_ranges: Optional[dict] = None
    ) -> list[ProblemVariant]:
        """
        Generer varianter av et derivasjonsproblem.
        
        Args:
            template: Mal med plassholdere, f.eks. "{a}*x**{n} + {b}*x"
            num_variants: Antall varianter
            difficulty: 0.0-1.0, påvirker tallstørrelser
            param_ranges: Egendefinerte områder for parametre
            
        Returns:
            Liste med ProblemVariant, hver med garantert korrekt svar
            
        Eksempel:
            >>> engine.generate_derivative_variants("{a}*x**{n}", 3)
            [
                ProblemVariant(problem="2x^3", answer="6x^2", ...),
                ProblemVariant(problem="5x^4", answer="20x^3", ...),
                ...
            ]
        """
        # Standard parameterområder basert på vanskelighetsgrad
        if param_ranges is None:
            if difficulty < 0.3:
                param_ranges = {
                    'a': range(1, 6),
                    'b': range(1, 6),
                    'c': range(1, 6),
                    'n': range(2, 4),
                    'm': range(1, 3),
                }
            elif difficulty < 0.7:
                param_ranges = {
                    'a': range(-10, 11),
                    'b': range(-10, 11),
                    'c': range(-10, 11),
                    'n': range(2, 6),
                    'm': range(1, 4),
                }
            else:
                param_ranges = {
                    'a': range(-20, 21),
                    'b': range(-20, 21),
                    'c': range(-20, 21),
                    'n': range(2, 8),
                    'm': range(1, 5),
                }
        
        # Finn hvilke parametre som brukes i malen
        param_pattern = r'\{(\w+)\}'
        used_params = set(re.findall(param_pattern, template))
        
        variants = []
        attempts = 0
        max_attempts = num_variants * 10
        
        while len(variants) < num_variants and attempts < max_attempts:
            attempts += 1
            
            # Generer tilfeldige verdier
            params = {}
            for param in used_params:
                if param in param_ranges:
                    value = random.choice(list(param_ranges[param]))
                    # Unngå 0 for koeffisienter
                    while value == 0 and param in ['a', 'b', 'c']:
                        value = random.choice(list(param_ranges[param]))
                    params[param] = value
                else:
                    params[param] = random.randint(1, 5)
            
            # Lag uttrykket
            try:
                expr_str = template.format(**params)
                expr = self.parse_expression(expr_str)
                
                # Beregn korrekt derivert
                derivative = diff(expr, self.x)
                derivative_simplified = simplify(derivative)
                
                variant = ProblemVariant(
                    problem_latex=self.to_latex(expr),
                    answer_latex=self.to_latex(derivative_simplified),
                    difficulty=difficulty,
                    parameters=params
                )
                
                # Sjekk at vi ikke har duplikater
                if not any(v.problem_latex == variant.problem_latex for v in variants):
                    variants.append(variant)
                    
            except Exception:
                continue
        
        return variants
    
    def generate_integral_variants(
        self,
        template: str,
        num_variants: int = 5,
        difficulty: float = 0.5,
        definite: bool = False,
        bounds: Optional[tuple] = None
    ) -> list[ProblemVariant]:
        """Generer varianter av integrasjonsproblemer."""
        # Lignende logikk som derivasjon
        param_ranges = {
            'a': range(1, 10) if difficulty < 0.5 else range(-15, 16),
            'b': range(1, 10) if difficulty < 0.5 else range(-15, 16),
            'n': range(1, 4) if difficulty < 0.5 else range(1, 6),
        }
        
        param_pattern = r'\{(\w+)\}'
        used_params = set(re.findall(param_pattern, template))
        
        variants = []
        attempts = 0
        
        while len(variants) < num_variants and attempts < num_variants * 10:
            attempts += 1
            
            params = {p: random.choice(list(param_ranges.get(p, range(1, 5)))) 
                     for p in used_params}
            
            # Unngå 0
            for p in ['a', 'b']:
                if p in params and params[p] == 0:
                    params[p] = 1
            
            try:
                expr_str = template.format(**params)
                expr = self.parse_expression(expr_str)
                
                if definite and bounds:
                    integral = integrate(expr, (self.x, bounds[0], bounds[1]))
                else:
                    integral = integrate(expr, self.x)
                
                integral_simplified = simplify(integral)
                answer = self.to_latex(integral_simplified)
                if not definite:
                    answer += " + C"
                
                variant = ProblemVariant(
                    problem_latex=self.to_latex(expr),
                    answer_latex=answer,
                    difficulty=difficulty,
                    parameters=params
                )
                
                if not any(v.problem_latex == variant.problem_latex for v in variants):
                    variants.append(variant)
                    
            except Exception:
                continue
        
        return variants


# =============================================================================
# SPESIALISERTE GENERATORER FOR VGS
# =============================================================================

class VGSMathGenerator:
    """
    Spesialisert generator for VGS-matematikk.
    Bygger på MathEngine, men med pedagogisk tilpassede maler.
    """
    
    def __init__(self):
        self.engine = MathEngine()
        
        # R1/R2 Derivasjons-maler
        self.derivative_templates = {
            'polynomial_easy': [
                "{a}*x**2 + {b}*x + {c}",
                "{a}*x**3 + {b}*x",
                "{a}*x**{n}",
            ],
            'polynomial_medium': [
                "{a}*x**4 + {b}*x**3 + {c}*x**2",
                "{a}*x**{n} + {b}*x**{m} + {c}",
            ],
            'product_rule': [
                "x**{n} * exp(x)",
                "x**{n} * sin(x)",
                "x**{n} * cos(x)",
                "({a}*x + {b}) * exp(x)",
            ],
            'quotient_rule': [
                "x**{n} / (x + {a})",
                "sin(x) / x",
                "exp(x) / x**{n}",
            ],
            'chain_rule': [
                "sin({a}*x + {b})",
                "exp({a}*x**2)",
                "ln({a}*x + {b})",
                "({a}*x + {b})**{n}",
                "sqrt({a}*x + {b})",
            ],
            'combined': [
                "x**{n} * sin({a}*x)",
                "exp(x) * ln(x)",
                "({a}*x**2 + {b}*x) * exp(x)",
            ]
        }
        
        # Integrasjonsmaler
        self.integral_templates = {
            'polynomial': [
                "{a}*x**{n}",
                "{a}*x**2 + {b}*x + {c}",
            ],
            'exponential': [
                "{a}*exp({b}*x)",
                "exp(x)",
            ],
            'trigonometric': [
                "{a}*sin({b}*x)",
                "{a}*cos({b}*x)",
            ],
            'substitution': [
                "x * exp(x**2)",
                "sin(x) * cos(x)",
                "x / (x**2 + {a})",
            ]
        }
    
    def generate_r1_derivative_set(
        self,
        category: str,
        num_problems: int = 5,
        difficulty: float = 0.5
    ) -> list[ProblemVariant]:
        """
        Generer et sett med derivasjonsoppgaver for R1.
        
        Args:
            category: 'polynomial_easy', 'product_rule', 'chain_rule', etc.
            num_problems: Antall oppgaver
            difficulty: 0.0-1.0
        """
        templates = self.derivative_templates.get(category, self.derivative_templates['polynomial_easy'])
        
        all_variants = []
        per_template = max(1, num_problems // len(templates))
        
        for template in templates:
            variants = self.engine.generate_derivative_variants(
                template,
                num_variants=per_template,
                difficulty=difficulty
            )
            all_variants.extend(variants)
        
        # Bland og begrens
        random.shuffle(all_variants)
        return all_variants[:num_problems]
    
    def generate_differentiated_set(
        self,
        topic: str,
        num_per_level: int = 4
    ) -> dict[str, list[ProblemVariant]]:
        """
        Generer tre nivåer av oppgaver for differensiering.
        
        Returns:
            {
                'nivå_1': [...],  # Grunnleggende
                'nivå_2': [...],  # Middels
                'nivå_3': [...],  # Utfordring
            }
        """
        if topic == 'derivasjon':
            return {
                'nivå_1': self.generate_r1_derivative_set('polynomial_easy', num_per_level, 0.2),
                'nivå_2': self.generate_r1_derivative_set('chain_rule', num_per_level, 0.5),
                'nivå_3': self.generate_r1_derivative_set('combined', num_per_level, 0.8),
            }
        else:
            # Fallback
            return {
                'nivå_1': [],
                'nivå_2': [],
                'nivå_3': [],
            }


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    engine = MathEngine()
    
    print("=== MaTultimate Math Engine ===\n")
    
    # Test derivasjon
    print("1. Verifiserer derivasjon:")
    result = engine.verify_derivative("x**3 + 2*x", "3*x**2 + 2")
    print(f"   f(x) = x³ + 2x, f'(x) = 3x² + 2: {result.is_correct}")
    
    # Test feil derivasjon
    result_wrong = engine.verify_derivative("x**3", "2*x**2")
    print(f"   f(x) = x³, f'(x) = 2x² (feil): {result_wrong.is_correct}")
    print(f"   Forventet: {result_wrong.expected}\n")
    
    # Test integrasjon
    print("2. Verifiserer integral:")
    result_int = engine.verify_integral("2*x", "x**2")
    print(f"   ∫2x dx = x²: {result_int.is_correct}\n")
    
    # Test variant-generering
    print("3. Genererer varianter av x^n:")
    variants = engine.generate_derivative_variants("{a}*x**{n}", 3, difficulty=0.3)
    for v in variants:
        print(f"   f(x) = {v.problem_latex}, f'(x) = {v.answer_latex}")
    
    print("\n4. Steg-for-steg løsning:")
    solution = engine.derivative_step_by_step("x**2 * exp(x)")
    for step in solution.steps:
        print(f"   {step.description}")
        print(f"   {step.expression}")
        if step.rule_applied:
            print(f"   [Regel: {step.rule_applied}]")
        print()
    
    print("=== Ferdig ===")
