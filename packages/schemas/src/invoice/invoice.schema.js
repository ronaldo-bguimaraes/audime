import { z } from "zod";
export const InvoiceItemSchema = z.object({
    description: z.string(),
    barcode: z.string().optional(),
    quantity: z.number().positive(),
    unit: z.string(),
    unitPrice: z.number().nonnegative(),
    totalPrice: z.number().nonnegative(),
});
