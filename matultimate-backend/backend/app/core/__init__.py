"""
MaTultimate Core
================
Kjernekomponenter for matematikkgenerering.
"""

from .math_engine import MathEngine, VGSMathGenerator, VerificationResult, StepByStepSolution
from .sanitizer import CodeSanitizer, sanitize, quick_strip, detect_format
from .compiler import DocumentCompiler, CompilationResult, DocumentFormat, TypstTemplates

__all__ = [
    'MathEngine',
    'VGSMathGenerator', 
    'VerificationResult',
    'StepByStepSolution',
    'CodeSanitizer',
    'sanitize',
    'quick_strip',
    'detect_format',
    'DocumentCompiler',
    'CompilationResult',
    'DocumentFormat',
    'TypstTemplates',
]
