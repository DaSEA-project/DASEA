## Github Actions Workflow Directory

### build_and_test.yml

Ran on every Pull Request and push to the main branch. Ensures no build errors and that the quick-executing miners still work.

### create_release.yml

Used to trigger the dataset release on Steve. Is ran manually via the (Github Actions UI)[https://github.com/DaSEA-project/DASEA/actions/workflows/create_release.yml]