import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ChatMessage, DoctorStatus, GenericResult, Patient, TwinResult } from "../types";

interface PortalState {
  patient: Patient | null;
  mode: "general" | "specialist" | null;
  chat: ChatMessage[];
  draft: string | null;
  originalDraft: string | null;
  twin: TwinResult | null;
  approved: string | null;
  rejected: boolean;
  doctorStatus: DoctorStatus;
  view: "Patient" | "Doctor";
}

interface AppState {
  theme: "light" | "dark";
  patient: Patient | null;
  genericResult: GenericResult | null;
  twinResult: TwinResult | null;
  portal: PortalState;
  setTheme: (theme: "light" | "dark") => void;
  setPatient: (patient: Patient) => void;
  setGenericResult: (result: GenericResult | null) => void;
  setTwinResult: (result: TwinResult | null) => void;
  savePortalIntake: (patient: Patient) => void;
  patchPortal: (partial: Partial<PortalState>) => void;
  resetPortalChat: () => void;
}

const emptyPortal: PortalState = {
  patient: null,
  mode: null,
  chat: [],
  draft: null,
  originalDraft: null,
  twin: null,
  approved: null,
  rejected: false,
  doctorStatus: null,
  view: "Patient",
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: "light",
      patient: null,
      genericResult: null,
      twinResult: null,
      portal: emptyPortal,
      setTheme: (theme) => set({ theme }),
      setPatient: (patient) => set({ patient, genericResult: null, twinResult: null }),
      setGenericResult: (genericResult) => set({ genericResult }),
      setTwinResult: (twinResult) => set({ twinResult }),
      savePortalIntake: (patient) =>
        set({
          patient,
          genericResult: null,
          twinResult: null,
          portal: { ...emptyPortal, patient },
        }),
      patchPortal: (partial) => set((state) => ({ portal: { ...state.portal, ...partial } })),
      resetPortalChat: () =>
        set((state) => ({
          portal: {
            ...state.portal,
            mode: null,
            chat: [],
            draft: null,
            originalDraft: null,
            twin: null,
            approved: null,
            rejected: false,
            doctorStatus: null,
            view: "Patient",
          },
        })),
    }),
    {
      name: "cardiotwin-session",
      version: 2,
      migrate: (persisted) => ({ ...(persisted as object), theme: "light" }),
    },
  ),
);
