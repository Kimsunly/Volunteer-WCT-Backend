"""Safe logging utility to prevent Unicode errors on Windows"""
import sys
import logging

# Configure logging to handle Unicode safely
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set encoding for stdout/stderr
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

def safe_print(*args, **kwargs):
    """Print function that safely handles Unicode on Windows"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: encode to ASCII and replace non-ASCII chars
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('ascii', 'replace').decode('ascii'))
            else:
                safe_args.append(str(arg))
        print(*safe_args, **kwargs)

logger = logging.getLogger(__name__)
