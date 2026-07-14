/*
 * This header provides IRQ_TYPE constants for device tree bindings.
 * These are used by interrupt-controller binding headers.
 */

#ifndef _DT_BINDINGS_INTERRUPT_CONTROLLER_INTERRUPTS_H
#define _DT_BINDINGS_INTERRUPT_CONTROLLER_INTERRUPTS_H

/* IRQ_TYPE values - these match Linux kernel IRQ_TYPE_* definitions */
#define IRQ_TYPE_NONE           0x0000
#define IRQ_TYPE_EDGE_RISING    0x0001
#define IRQ_TYPE_EDGE_FALLING   0x0002
#define IRQ_TYPE_EDGE_BOTH      0x0003
#define IRQ_TYPE_LEVEL_HIGH     0x0004
#define IRQ_TYPE_LEVEL_LOW      0x0008
#define IRQ_TYPE_LEVEL_MASK     0x000f

#endif /* _DT_BINDINGS_INTERRUPT_CONTROLLER_INTERRUPTS_H */