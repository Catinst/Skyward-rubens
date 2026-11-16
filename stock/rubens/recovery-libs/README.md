# recovery-libs（历史材料）

这里的三个库（`libbinder.so`、`libvintf.so`、`android.hidl.token@1.0.so`）是最初尝试把库直接塞进 ramdisk 的方案，**当前构建不再使用**：库改为开机时由 Skyward 从已安装系统复制到 `/system/lib64`（见 `devices/rubens.toml` 的 `recovery_libraries`），不占 initrd 体积。

另外，早期选用的 VNDK31 版 `libbinder.so` 与系统侧服务不兼容（接口头副本名不同，调用被以 `BAD_TYPE` 拒绝），后来改用已安装系统的 libbinder。

这些文件仅作历史参考，`SHA256SUMS` 和 `provenance.json` 记录它们当时的来源。