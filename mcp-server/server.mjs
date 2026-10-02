import { readFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";


const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, "..", "data");

const rates = JSON.parse(readFileSync(join(DATA_DIR, "rates.json"), "utf-8"));
const carriers = JSON.parse(readFileSync(join(DATA_DIR, "carriers.json"), "utf-8"));

console.error(`Loaded ${rates.length} rates and ${carriers.length} carriers`);


function lookupRate(carrierCode, origin, destination, weightLbs) {
    const carrier = carriers.find(c => c.carrier_code === carrierCode);
  
    const matches = rates.filter(r =>
      r.carrier_code === carrierCode &&
      r.origin.toLowerCase() === origin.toLowerCase() &&
      r.destination.toLowerCase() === destination.toLowerCase() &&
      weightLbs >= r.weight_min_lbs &&
      weightLbs <= r.weight_max_lbs
    );
  
    return {
      carrier: carrier ?? null,
      rates: matches,
    };
  }


const server = new McpServer({ name: "freight-rate-tool", version: "1.0.0" });

server.registerTool(
  "getRate",
  {
    description: "Looks up the exact freight rate for a carrier, lane (origin to destination), and shipment weight. Returns the raw rate record(s) and the carrier's status exactly as stored, including expired rates and inactive carriers. Does not judge validity.",
    inputSchema: {
      carrier_code: z.string().describe("Carrier code, e.g. FXFE"),
      origin: z.string().describe("Origin city and state, e.g. 'Chicago, IL'"),
      destination: z.string().describe("Destination city and state, e.g. 'Atlanta, GA'"),
      weight_lbs: z.number().describe("Shipment weight in pounds"),
    },
  },
  async ({ carrier_code, origin, destination, weight_lbs }) => ({
    content: [{ type: "text", text: JSON.stringify(lookupRate(carrier_code, origin, destination, weight_lbs)) }],
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);


  