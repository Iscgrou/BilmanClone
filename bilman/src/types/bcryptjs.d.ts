declare module 'bcryptjs' {
    /**
     * Generate a hash for the plaintext password
     */
    export function hash(s: string, salt: string | number): Promise<string>;
    
    /**
     * Compare plaintext password with hash
     */
    export function compare(s: string, hash: string): Promise<boolean>;
    
    /**
     * Generate a salt for the hash function
     */
    export function genSalt(rounds?: number): Promise<string>;
    
    /**
     * Generate a hash sync for the plaintext password
     */
    export function hashSync(s: string, salt: string | number): string;
    
    /**
     * Compare plaintext password with hash sync
     */
    export function compareSync(s: string, hash: string): boolean;
    
    /**
     * Generate a salt for the hash function sync
     */
    export function genSaltSync(rounds?: number): string;
}
