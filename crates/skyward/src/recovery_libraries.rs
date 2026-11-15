//! Prepare the libraries missing from the recovery before its services run.

use anyhow::{Context, Result};
use std::path::Path;

/// Copy the named libraries atomically beside the recovery's own libraries.
/// Renaming a fresh inode keeps a running program's old mapping valid.
pub fn copy(libraries: &[String], directory: &Path) -> Result<()> {
    for library in libraries {
        let from = Path::new(library);
        let name = from.file_name().with_context(|| format!("{library} names no library"))?;
        let to = directory.join(name);
        anyhow::ensure!(from != to, "{library} is already the recovery library");
        let mut part = to.clone().into_os_string();
        part.push(".part");
        let prepared = (|| {
            std::fs::copy(from, &part).with_context(|| format!("copy {library} to {}", Path::new(&part).display()))?;
            std::fs::rename(&part, &to).with_context(|| format!("put {} in place", to.display()))
        })();
        if prepared.is_err() {
            let _ = std::fs::remove_file(&part);
        }
        prepared?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn prepares_named_libraries_and_preserves_the_rest() {
        let work = tempfile::tempdir().unwrap();
        let source = work.path().join("source");
        let recovery = work.path().join("recovery");
        std::fs::create_dir(&source).unwrap();
        std::fs::create_dir(&recovery).unwrap();
        let binder = source.join("libbinder.so");
        std::fs::write(&binder, b"matching binder").unwrap();
        std::fs::write(recovery.join("libc.so"), b"original libc").unwrap();
        let wanted = [binder.to_string_lossy().into_owned()];
        copy(&[], &recovery).unwrap();
        assert!(!recovery.join("libbinder.so").exists());
        std::fs::write(recovery.join("libbinder.so"), b"old binder").unwrap();
        let mut old = std::fs::File::open(recovery.join("libbinder.so")).unwrap();
        copy(&wanted, &recovery).unwrap();
        let mut held = Vec::new();
        std::io::Read::read_to_end(&mut old, &mut held).unwrap();
        assert_eq!(held, b"old binder");
        copy(&wanted, &recovery).unwrap();
        assert_eq!(std::fs::read(recovery.join("libbinder.so")).unwrap(), b"matching binder");
        assert_eq!(std::fs::read(recovery.join("libc.so")).unwrap(), b"original libc");
        assert!(!recovery.join("libbinder.so.part").exists());
        assert!(copy(&[source.join("missing.so").to_string_lossy().into_owned()], &recovery).is_err());
    }
}
