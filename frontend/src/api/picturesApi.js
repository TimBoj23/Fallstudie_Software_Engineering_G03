import { apiUpload } from "./client";

export function uploadPicture(file) {
  const formData = new FormData();
  formData.append("file", file);
  return apiUpload("/pictures", formData);
}
