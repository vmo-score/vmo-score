from invoke import Collection, task
from invoke.util import log

@task
def clean(ctx):
    """remove build artifacts."""
    ctx.run('rm -rf build/')
    ctx.run('rm -rf dist/')
    ctx.run('rm -rf {}'.format(ctx.sphinx.target))
    ctx.run('rm -rf VMO_Score.egg-info')
    ctx.run('rm -rf htmlcov')
    ctx.run('find . -name __pycache__ -delete')
    ctx.run('find . -name *.pyc -delete')
    ctx.run('find . -name *.pyo -delete')
    ctx.run('find . -name *~ -delete')

    log.info('cleaned up')


@task
def test(ctx):
    """run the test runner."""
    ctx.run('py.test --pylama '
        '--cov-report html --cov-report term-missing '
        '--cov=VMO_Score tests/', pty=True)


@task
def build_docs(ctx):
    """generate the documentation."""
    ctx.run("sphinx-build -b html -d {0}/doctrees docs {0}".format(ctx.sphinx.target))


@task
def lint(ctx):
    """check style with pylama."""
    ctx.run('pylama VMO_Score')


@task(pre=[clean])
def build(ctx):
    """build the module"""
    ctx.run('python setup.py build', pty=True)

    log.info('build vmo-score')

ns = Collection()
ns.add_task(build_docs, "docs")
ns.configure({'sphinx': {'target': "docs/_build"}})
