from conan.tools.files import copy
import os


def deploy(graph, output_folder, **kwargs):
    conanfile = graph.root.conanfile
    conanfile.output.info(f"AliceVision deployer to {output_folder}")
    for dep in conanfile.dependencies.values():
        if dep.package_folder is None:
            continue
        _deploy_single(dep, conanfile, output_folder, dep.ref.name == "alicevision")
        
def _deploy_single(dep, conanfile, output_folder, include_bin):
    new_folder = output_folder
    rmdir(new_folder)
    symlinks = conanfile.conf.get("tools.deployer:symlinks", check_type=bool, default=True)
    try:
        if include_bin:
            shutil.copytree(os.path.join(dep.package_folder, "bin"), os.path.join(new_folder, "bin"), symlinks=symlinks)            
        shutil.copytree(os.path.join(dep.package_folder, "lib"), os.path.join(new_folder, "lib"), symlinks=symlinks)
    except Exception as e:
        if "WinError 1314" in str(e):
            ConanOutput().error("full_deploy: Symlinks in Windows require admin privileges "
                                "or 'Developer mode = ON'", error_type="exception")
        raise ConanException(f"full_deploy: The copy of '{dep}' files failed: {e}.\nYou can "
                             f"use 'tools.deployer:symlinks' conf to disable symlinks")
    dep.set_deploy_folder(new_folder)