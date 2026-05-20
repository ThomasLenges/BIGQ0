/* Auto-generated linker script fragment for LLEXT
 * Separates .rodata sections based on relocation status
 */

SECTIONS
{
    /* Read-only data WITH relocations - will be copied to RAM by LLEXT */
    .rodata : {
        *(.rodata._ZL12arduino_pins)
    }

    /* Read-only data WITHOUT relocations - kept in flash by LLEXT */
    .llext.rodata.noreloc : {
        *(.rodata.str1.1)
    }

    /* Merge all .rel.rodata.* sections into .rel.rodata */
    .rel.rodata : {
        *(.rel.rodata)
        *(.rel.rodata.*)
    }

    /* Merge all .rela.rodata.* sections into .rela.rodata */
    .rela.rodata : {
        *(.rela.rodata)
        *(.rela.rodata.*)
    }

}
