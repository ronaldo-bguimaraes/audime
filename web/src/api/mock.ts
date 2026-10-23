import { setupMockApi as sharedSetupMock } from "shared";
import { api } from "./client";

export function setupMockApi() {
  sharedSetupMock(api);
}
