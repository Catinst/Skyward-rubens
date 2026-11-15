# Redmi K50（rubens）首版构建

本 fork 以 BkaNeko/xaga-skyward 的联发科适配为基础，为 Redmi K50（rubens / Dimensity 8100）构建 Skyward vendor_boot 镜像。处于适配阶段，尚未真机验证启动、显示、触控、解密或网络。

## 构建输入

- 原版 OS1 vendor_boot：由设备持有者提供，ramdisk 属性 V816.0.14.0.ULNCNXM；详见 [基底说明](stock/rubens/README.md)。
- 没有合入 ColorOS `my_*` fstab 补丁，first-stage fstab 和 Recovery fstab 均保留原版。
- 输出是完整 64 MiB vendor_boot 分区镜像，不是 boot 或独立 recovery 镜像。
- 设备配置见 [rubens.toml](devices/rubens.toml)：1440×3200、密度480、6.67英寸，保留默认刷新率及触控驱动行为。
- TEE/WLAN 参数按本机 vendor init 核对，实际 Recovery 功能仍待验证。
- 全局节点权限交接复用 xaga 的限时等待，避免驱动节点较晚出现时遗漏权限设置。

## GitHub Actions 构建

推送后自动执行测试、lint 和 rubens 构建。也可以手动运行：

```sh
gh workflow run build.yml --repo Catinst/Skyward-rubens --ref main -f device=rubens
```

流程使用 Rust 1.100.0、NDK r29、cargo-ndk 4.1.2，并完成：

1. 编译 skyward、静态 system-init 和电脑端 skyward-pack。
2. 解压仓库内原版镜像，验证 SHA-256。
3. 使用 rubens 配置打包。
4. 检查输出64 MiB、AVB范围、DTB及启动配置未变。
5. 逐字节比较两份 fstab、Recovery模块加载列表，确认未改变；比较 Recovery 程序和设备配置确为本次输入。
6. 上传镜像 zip 为 Actions artifact，保留7天。

构建阶段不连接或刷写设备。打包器生成未签名的 AVB footer；镜像能够构建不代表设备 BL 状态允许刷写或功能已经验证。本 fork 没有执行手机端 filesystem/encryption 测试。
