export const MOCK_ANALYTICS = {
  totalQueries: {
    value: "24,592",
    trend: "+12.5%",
    isPositive: true,
  },
  avgResponseTime: {
    value: "1.2s",
    trend: "-0.3s",
    isPositive: true, // Lower is better
  },
  resolutionRate: {
    value: "84%",
    trend: "+2.1%",
    isPositive: true,
  },
  escalationRate: {
    value: "16%",
    trend: "-2.1%",
    isPositive: true, // Lower is better
  },
  queriesByDay: [
    { name: "Mon", value: 3400 },
    { name: "Tue", value: 4100 },
    { name: "Wed", value: 3800 },
    { name: "Thu", value: 4500 },
    { name: "Fri", value: 5200 },
    { name: "Sat", value: 2100 },
    { name: "Sun", value: 1492 },
  ],
  topAgents: [
    { name: "Support Persona (Default)", queries: 15420 },
    { name: "Technical Troubleshooting", queries: 6210 },
    { name: "Billing Inquiry", queries: 2962 },
  ],
};
