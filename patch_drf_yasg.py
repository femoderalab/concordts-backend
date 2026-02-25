# patch_drf_yasg.py
import os
import site
import sys

# Find the drf_yasg installation path
site_packages = site.getsitepackages()[0]
init_file = os.path.join(site_packages, 'drf_yasg', '__init__.py')

# Read the file
with open(init_file, 'r') as f:
    content = f.read()

# Replace the pkg_resources import with a try/except block
new_content = content.replace(
    'from pkg_resources import DistributionNotFound, get_distribution',
    '''try:
    from pkg_resources import DistributionNotFound, get_distribution
except ImportError:
    # Fallback for Python 3.14+ where setuptools might not be available
    import importlib.metadata
    DistributionNotFound = ImportError
    def get_distribution(dist_name):
        try:
            return importlib.metadata.distribution(dist_name)
        except importlib.metadata.PackageNotFoundError:
            raise DistributionNotFound(f"Package {dist_name} not found")'''
)

# Write back
with open(init_file, 'w') as f:
    f.write(new_content)

print("✅ drf-yasg patched successfully for Python 3.14+")