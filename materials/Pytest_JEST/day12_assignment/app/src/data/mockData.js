export const departments = [
    { id: 1, name: "Engineering" },
    { id: 2, name: "Marketing" },
    { id: 3, name: "Human Resources" },
    { id: 4, name: "Finance" },
    { id: 5, name: "Sales"}
]

export const projects = [
  { id: 1, name: "Website Redesign", status: "Active", employeeIds: [1, 3, 5] },
  { id: 2, name: "Mobile App", status: "Active", employeeIds: [2, 4] },
  { id: 3, name: "Data Migration", status: "Active", employeeIds: [1, 6] },
  { id: 4, name: "Cloud Infrastructure", status: "Completed", employeeIds: [3, 7] },
  { id: 5, name: "AI Chatbot", status: "Active", employeeIds: [2, 5, 8] },
];

export const employees = [
  { id: 1, name: "Tanaka Yuki", email: "tanaka@company.com", departmentId: 1, projectIds: [1, 3] },
  { id: 2, name: "Suzuki Hana", email: "suzuki@company.com", departmentId: 2, projectIds: [2, 5] },
  { id: 3, name: "Sato Kenji", email: "sato@company.com", departmentId: 1, projectIds: [1, 4] },
  { id: 4, name: "Yamamoto Aoi", email: "yamamoto@company.com", departmentId: 3, projectIds: [2] },
  { id: 5, name: "Watanabe Ren", email: "watanabe@company.com", departmentId: 4, projectIds: [1, 5] },
  { id: 6, name: "Ito Sakura", email: "ito@company.com", departmentId: 1, projectIds: [3] },
  { id: 7, name: "Nakamura Daiki", email: "nakamura@company.com", departmentId: 5, projectIds: [4] },
  { id: 8, name: "Kobayashi Mei", email: "kobayashi@company.com", departmentId: 2, projectIds: [5] },
];


