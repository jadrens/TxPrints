import subprocess

command_base = ".\\tools\\imdisk\\imdisk.exe"

class MemDisk:
    is_mounted: bool = False
    def mount_mem_disk(self) -> None:
        cmd = f"{command_base} -a -s {self.size} -m {self.driver_letter}: -p \"/fs:NTFS /q /y\""
        return_num = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        if return_num != 0:
            raise RuntimeError("Failed to mount memory disk.")
        else:
            self.is_mounted = True
    def unmount_mem_disk(self) -> None:
        cmd = f"{command_base} -D -m {self.driver_letter}:"
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')

        self.is_mounted = False

    def __init__(self, size="512M", driver_letter="Z") -> None:
        self.driver_letter = driver_letter
        self.size = size
    
    def get_file_path(self, filename: str) -> str:
        if not self.is_mounted:
            raise RuntimeError("Memory disk is not mounted.")
        return f"{self.driver_letter}:{'\\'}{filename}"
    