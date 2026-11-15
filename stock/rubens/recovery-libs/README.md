# Recovery 服务管理器缺失库

首版真机直接 logcat 证明：`/system/bin/servicemanager` 因 `libbinder.so` 缺失无法链接，以状态1重复退出，约25秒后触发init critical重启。原版ramdisk的servicemanager还依赖缺失的libvintf；hwservicemanager缺android.hidl.token@1.0。

本目录为最小修复集合，不补整个当前Android15系统库目录，不替换原版libc/libutils/linker。

| 库 | 来源 |
|---|---|
| libbinder.so | 本机 `/apex/com.android.vndk.v31/lib64/libbinder.so`，从设备只读导出 |
| libvintf.so | 原厂 rubens OS2.0.3.0.ULNCNXM OTA的system分区 `/system/lib64/libvintf.so` |
| android.hidl.token@1.0.so | 同一原厂OTA system分区 `/system/lib64/android.hidl.token@1.0.so` |

原厂OTA system分区SHA-256：a40eb32d71a6320406aef2eee25ea5ec3f5ca7f0b3c4be076281c1269b42f0e1，已按payload元数据验证。各库SHA-256见SHA256SUMS，构建前验证，打包后逐字节核对。

已离线检查这些库及原版servicemanager/hwservicemanager的DT_NEEDED和强未定义动态符号，组合没有未满足项；这不等价于完整ABI及功能验证。当前Android15同名libbinder/libvintf有原版Recovery无法满足的符号，原厂OTA libbinder也依赖原版libutils缺失的移动构造符号，因此选用VNDK31 Binder。

库打包到 `/skyward/recovery-libs`，挂载系统分区成功后、运行硬件命名程序及启动servicemanager之前，按设备recovery_libraries配置复制到 `/system/lib64`。复制失败保留UI并跳过设备服务初始化，不启动依赖不完整的critical服务。原厂fstab不修改。

范围：修复服务管理器依赖并验证Recovery稳定性；gatekeeperd、keystore2等原版程序还有其他库缺口，解密并未因此获得验证。不得将此目录解释为完整解密依赖集合。
