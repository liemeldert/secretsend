import CryptoJS from 'crypto-js';

export class EncryptedPassword {
  key: string;
  encryptedPassword = "";
  decryptedPassword = "";
  URL = "";

  constructor(password: string = "", key: string = "") {
    this.key = key || this.generateKey();
    
    if (password) {
      this.encryptedPassword = this.encryptPassword(password);
    } else {
      this.decryptedPassword = this.decryptPassword(password);
    }
  }

  private generateKey(): string {
    const array = new Uint8Array(64);
    window.crypto.getRandomValues(array);
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
    return Array.from(
      array,
      (byte) => characters[byte % characters.length]
    ).join("");
  }

  private encryptPassword(password: string): string {
    return CryptoJS.AES.encrypt(password, this.key).toString();
  }

  private decryptPassword(password: string): string {
    return CryptoJS.AES.decrypt(password, this.key).toString(CryptoJS.enc.Utf8);
  }

  generateLink(id: string): string {
    const currentDomain = window.location.origin;
    return `${currentDomain}/decrypt/${id}/${this.key}`;
  }
}
