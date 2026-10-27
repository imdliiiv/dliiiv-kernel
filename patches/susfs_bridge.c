// SPDX-License-Identifier: GPL-2.0
/*
 * SUSFS Linkage Bridge for BakaSU on ACK 6.6
 * Provides globally exported symbols required by kernel-side SUSFS hooks.
 */

#include <linux/fs.h>
#include <asm-generic/errno-base.h>

struct user_arg_ptr;

extern int ksu_handle_selinux_setprocattr(const char *name, void *value, size_t size);

int my_setprocattr(const char *name, void *value, size_t size)
{
    return ksu_handle_selinux_setprocattr(name, value, size);
}

int ksu_setup_preinit_file(struct filename **filename_ptr, struct user_arg_ptr *argv_user)
{
    return -EINVAL;
}

int ksu_preinit_handle_post_execveat(int *fd, struct filename **filename_ptr,
                                     void *argv_user, void *envp_user,
                                     int *flags, int *retval, int *preinit_fd)
{
    return 0;
}
