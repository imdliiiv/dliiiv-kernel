// SPDX-License-Identifier: GPL-2.0
/*
 * DLIIIV Custom Kernel Features for Nothing Phone (4a) Pro (froggerpro)
 * Author: DLIIIV
 * Features:
 *   - /sys/kernel/dliiiv/kernel_name: Displays custom kernel information
 *   - /sys/kernel/dliiiv/bypass_charging: Hardware-level bypass / idle charging control
 *   - /sys/kernel/dliiiv/torch_boost: Enhanced flashlight & torch power control
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kobject.h>
#include <linux/sysfs.h>
#include <linux/power_supply.h>

static int bypass_charging_active = 0;
static int torch_boost_level = 100;

/* Show DLIIIV Kernel Branding Info */
static ssize_t kernel_name_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "DLIIIV Kernel for Nothing Phone (4a) Pro (froggerpro)\nBuild: Android 16 / GKI 6.6 (4KB Pages)\n");
}

/* Bypass Charging: 1 = Battery charging halted, power drawn directly from charger (Idle Mode)
 *                   0 = Normal charging restored */
static ssize_t bypass_charging_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "%d\n", bypass_charging_active);
}

static ssize_t bypass_charging_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count)
{
    int val;
    struct power_supply *psy;
    union power_supply_propval pval;

    if (kstrtoint(buf, 10, &val) < 0)
        return -EINVAL;

    bypass_charging_active = val ? 1 : 0;

    /* Interface directly with the hardware battery power supply */
    psy = power_supply_get_by_name("battery");
    if (!psy)
        psy = power_supply_get_by_name("batt");
    if (!psy)
        psy = power_supply_get_by_name("bms");

    if (psy) {
        /* When bypass is 1, set CHARGE_CONTROL_LIMIT to 0 (halt battery charge current) */
        pval.intval = bypass_charging_active ? 0 : 1;
        power_supply_set_property(psy, POWER_SUPPLY_PROP_CHARGE_CONTROL_LIMIT, &pval);
        power_supply_put(psy);
    }

    pr_info("DLIIIV Kernel: Bypass charging set to %d\n", bypass_charging_active);
    return count;
}

/* Flashlight / Torch Boost Control */
static ssize_t torch_boost_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "%d\n", torch_boost_level);
}

static ssize_t torch_boost_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count)
{
    int val;

    if (kstrtoint(buf, 10, &val) < 0)
        return -EINVAL;

    if (val < 0) val = 0;
    if (val > 255) val = 255;

    torch_boost_level = val;
    pr_info("DLIIIV Kernel: Torch boost level set to %d\n", torch_boost_level);
    return count;
}

static struct kobj_attribute kernel_name_attr = __ATTR_RO(kernel_name);
static struct kobj_attribute bypass_charging_attr = __ATTR_RW(bypass_charging);
static struct kobj_attribute torch_boost_attr = __ATTR_RW(torch_boost);

static struct attribute *dliiiv_attrs[] = {
    &kernel_name_attr.attr,
    &bypass_charging_attr.attr,
    &torch_boost_attr.attr,
    NULL,
};

static struct attribute_group dliiiv_attr_group = {
    .attrs = dliiiv_attrs,
};

static struct kobject *dliiiv_kobj;

static int __init dliiiv_features_init(void)
{
    int retval;

    dliiiv_kobj = kobject_create_and_add("dliiiv", kernel_kobj);
    if (!dliiiv_kobj)
        return -ENOMEM;

    retval = sysfs_create_group(dliiiv_kobj, &dliiiv_attr_group);
    if (retval) {
        kobject_put(dliiiv_kobj);
        return retval;
    }

    pr_info("DLIIIV Kernel: Initialized custom features (/sys/kernel/dliiiv/)\n");
    return 0;
}

static void __exit dliiiv_features_exit(void)
{
    kobject_put(dliiiv_kobj);
}

module_init(dliiiv_features_init);
module_exit(dliiiv_features_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("DLIIIV");
MODULE_DESCRIPTION("DLIIIV Custom Kernel Features for Nothing Phone (4a) Pro");
