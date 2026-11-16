# rubens 构建基底

本目录保存设备持有者提供的原版 OS1 `vendor_boot` 的 XZ 无损压缩副本，供 GitHub Actions 重复构建使用。它不是从小米服务器下载的完整更新包，也没有合入 ColorOS `my_*` fstab 补丁。

| 项目 | 值 |
| --- | --- |
| 设备 | Redmi K50 / rubens |
| recovery 分区 | `vendor_boot`（A/B） |
| ramdisk 版本属性 | V816.0.14.0.ULNCNXM |
| 构建标记 | OS1.0.14.0.ULNCNXM |
| 解压大小 | 67,108,864 字节 |
| 解压 SHA-256 | 518f97f578fcc096c2eb54ba96e9bc7e37cee8d8b717bf0ae87f19bd3b814758 |
| XZ SHA-256 | 1f5c47011cf4a4389540b6b2908be7b52705476ca715d0fac372f246e0379917 |

版本标记来自输入镜像自身的属性；这份副本没有用外部官方下载的镜像哈希独立核对过。

在仓库根目录恢复并校验：

```sh
xz -dc stock/rubens/vendor_boot.img.xz > stock/rubens/vendor_boot.img
echo '518f97f578fcc096c2eb54ba96e9bc7e37cee8d8b717bf0ae87f19bd3b814758  stock/rubens/vendor_boot.img' | sha256sum --check
```

构建流程保留原版的 first-stage fstab、Recovery fstab、DTB 和模块列表；生成的镜像是完整的 `vendor_boot` 分区镜像，AVB footer 由打包器重新生成且未签名。`skyward-servicemanager-override.rc` 是构建时加入的 init 覆盖，用于让 recovery 的 servicemanager 去掉 `critical` 并带上库路径。

本目录只有在 CI 的 `recovery` 作业里被使用；真机测试记录见仓库工作区的 `Skyward-rubens记录.md`。