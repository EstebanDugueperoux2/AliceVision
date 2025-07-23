import os
from re import match

# See https://github.com/conan-io/hooks/issues/486

def pre_build(output, conanfile, **kwargs):
    assert conanfile
    try:
        useCcache = list(filter(lambda v: match('ccache*', v), conanfile.tool_requires))
        if useCcache:
            os.environ["CCACHE_STATSLOG"] = "/tmp/stats_log.log"
    except:
        output.info("An exception occurred")



def post_build(output, conanfile, **kwargs):
    assert conanfile
    try:
        useCcache = list(filter(lambda v: match('ccache*', v), conanfile.tool_requires))
        if useCcache:
           output.info("ccache log stats:")
           conanfile.run("ccache --show-log-stats")
    except subprocess.CalledProcessError as e:
        output.warn(e.output)
    except:
        output.info("An exception occurred")