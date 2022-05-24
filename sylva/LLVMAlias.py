from llvmlite.ir import NamedValue # type: ignore


class Alias(NamedValue):

    name_prefix = '@'
    deduplicate_name = False

    def __init__(
        self,
        module,
        name,
        target,
        linkage='external',
        storage_class='default',
        visibility='default',
        preemption='local',
        thread_local='localexec',
        unnamed_addr='default',
        partition=None
    ):
        super().__init__(parent=module, type=target.type, name=name)
        self.target = target
        self.linkage = linkage
        self.storage_class = storage_class
        self.visibility = visibility
        self.preemption = preemption
        self.thread_local = thread_local
        self.unnamed_addr = unnamed_addr
        self.partition = partition

    def __str__(self):
        buf = [f'@{self.name}', '=']
        if self.linkage:
            buf.append(self.linkage)
        if self.preemption:
            buf.append(self.preemption)
        if self.visibility:
            buf.append(self.visibility)
        if self.storage_class:
            buf.append(self.storage_class)
        if self.thread_local:
            buf.append(self.thread_local)
        if self.unnamed_addr:
            buf.append(self.unnamed_addr)
        buf.extend(['alias', self.name, f'@{self.target}'])
        if self.partition:
            buf.extend([',', 'partition', self.partition])
        return ' '.join(buf)
