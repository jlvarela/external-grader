import sys
import settings
# debe ser llamado como package
# python -m grader_engine
from .grade_engine import main

sys.exit(main())