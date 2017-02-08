# coding: utf-8

import posixpath
from fabric.api import parallel, task, run
from fabric.state import env
from essay.tasks import virtualenv, package, fs
import supervisor
from contextlib import contextmanager
from os import path
from fabric.context_managers import prefix

__all__ = ['deploy']


@task(default=True)
@parallel(30)
def deploy(version, venv_dir, profile):
    """
    发布指定的版本

    会自动安装项目运行所需要的包
    """

    virtualenv.ensure(venv_dir)
    with virtualenv.activate(venv_dir):
        supervisor.ensure(project=env.PROJECT, profile=profile)
        package.install(env.PROJECT, version)
        supervisor.shutdown()
        supervisor.start()


@task(default=True)
@parallel(30)
def deploy_rq(version, profile):
    """
    发布指定的版本

    会自动安装项目运行所需要的包
    """
    venv_dir = env.RQ_PATH
    ensure_rq(venv_dir)

    with activate_rq(venv_dir):
        supervisor.ensure_rq(project='rq_starmachine', profile=profile)
        package.install(env.PROJECT, version)
        supervisor.shutdown_rq(venv_dir)
        supervisor.start_rq(venv_dir)

def ensure_rq(venv_dir):
    if virtualenv.is_virtualenv(venv_dir):
        return

    if package.is_virtualenv_installed_in_system():
        virtualenv_bin = 'virtualenv'
    else:
        virtualenv_bin = '~/.local/bin/virtualenv'
    print virtualenv_bin
    command = '%(virtualenv_bin)s --quiet "%(venv_dir)s"' % locals()
    run(command)

    sub_dirs = ['logs', 'etc', 'tmp']

    if 'VIRTUALENV_SUB_DIRS' in env:
        sub_dirs = list(set(sub_dirs + env.VIRTUALENV_SUB_DIRS))

    for sub_dir in sub_dirs:
        fs.ensure_dir(path.join(venv_dir, sub_dir))

@contextmanager
def activate_rq(venv_dir, local=False):
    """
    用来启用VirtualEnv的上下文管理器

    ::
        with virtualenv('/path/to/virtualenv'):
            run('python -V')

    .. _virtual environment: http://www.virtualenv.org/
    """

    if not virtualenv.is_virtualenv(venv_dir):
        raise Exception(u'无效虚拟环境: %s' % venv_dir)

    join = path.join if local else posixpath.join
    with prefix('. "%s"' % join(venv_dir, 'bin', 'activate')):
        env.CURRENT_VIRTUAL_ENV_DIR = venv_dir
        yield
        # del env['CURRENT_VIRTUAL_ENV_DIR']
