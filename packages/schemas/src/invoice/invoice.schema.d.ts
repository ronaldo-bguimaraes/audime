import { z } from "zod";
export declare const InvoiceItemSchema: z.ZodObject<{
    description: z.ZodString;
    barcode: z.ZodOptional<z.ZodString>;
    quantity: z.ZodNumber;
    unit: z.ZodString;
    unitPrice: z.ZodNumber;
    totalPrice: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    description: string;
    quantity: number;
    unit: string;
    unitPrice: number;
    totalPrice: number;
    barcode?: string | undefined;
}, {
    description: string;
    quantity: number;
    unit: string;
    unitPrice: number;
    totalPrice: number;
    barcode?: string | undefined;
}>;
