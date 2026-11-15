# rubens 构建基底

本目录保存设备持有者提供的原版 OS1 vendor_boot 的 XZ 无损压缩副本，供本 fork 的 GitHub Actions 重复构建使用。不是 OS2 OTA 中的镜像，也没有合入 ColorOS `my_*` fstab 补丁。

| 项目 | 值 |
|---|---|
| 设备 | Redmi K50 / rubens |
| ramdisk 版本属性 | V816.0.14.0.ULNCNXM |
| 构建标记 | OS1.0.14.0.ULNCNXM |
| 解压大小 | 67,108,864 字节 |
| 解压 SHA-256 | 518f97f578fcc096c2eb54ba96e9bc7e37cee8d8b717bf0ae87f19bd3b814758 |
| XZ SHA-256 | 1f5c47011cf4a4389540b6b2908be7b52705476ca715d0fac372f246e0379917 |

版本标记来自输入镜像自身属性。该副本未通过外部官方下载哈希独立认证。

在 Linux 仓库根目录恢复并校验：

```sh
xz -dc stock/rubens/vendor_boot.img.xz > /tmp/rubens-vendor_boot.img
echo '518f97f578fcc096c2eb54ba96e9bc7e37cee8d8b717bf0ae87f19bd3b814758  /tmp/rubens-vendor_boot.img' | sha256sum --check
```

构建流程保留 first-stage fstab、Recovery fstab、DTB 和原有模块。生成的镜像包含整个 vendor_boot 分区，AVB footer 由打包器重新生成且未签名。尚未真机验证启动、触控、解密和网络。
