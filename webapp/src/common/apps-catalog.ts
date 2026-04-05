import {
    Github,
    Bot,
    Archive,
    Database,
    Cpu,
    Gamepad2,
    BookOpen,
    Tv,
    Layout,
    Layers,
    Box,
    Edit3,
    Home,
    Search,
    Activity,
    Mail,
    LucideIcon
} from 'lucide-react';

export interface AppEntry {
    id: string;
    label: string;
    description: string;
    icon: LucideIcon;
    url: string;
    port: number;
    tags: string[];
}

// Full SOTA App Catalog - Comprehensive Federation Registry
export const APPS_CATALOG: AppEntry[] = [
    {
        id: 'universal-actuator',
        label: 'Actuator Hub',
        description: 'Federated domain gateway and tool router (SOTA Core)',
        icon: Bot,
        url: 'http://localhost:10854',
        port: 10854,
        tags: ['core', 'gateway']
    },
    {
        id: 'git-github',
        label: 'Git & GitHub',
        description: 'Repository management and version control',
        icon: Github,
        url: 'http://localhost:10702',
        port: 10702,
        tags: ['dev', 'scm']
    },
    {
        id: 'advanced-memory',
        label: 'Advanced Memory',
        description: 'Semantic knowledge base and long-term context',
        icon: BookOpen,
        url: 'http://localhost:10704',
        port: 10704,
        tags: ['core', 'knowledge']
    },
    {
        id: 'filesystem-hub',
        label: 'Filesystem Hub',
        description: 'Universal file operations and audit logs',
        icon: Archive,
        url: 'http://localhost:10743',
        port: 10743,
        tags: ['utility', 'files']
    },
    {
        id: 'db-ops',
        label: 'Database Ops',
        description: 'SQL/NoSQL query lab and schema manager',
        icon: Database,
        url: 'http://localhost:10708',
        port: 10708,
        tags: ['dev', 'data']
    },
    {
        id: 'local-llm',
        label: 'Local LLM Stack',
        description: 'RTX 4090 inference and model management',
        icon: Cpu,
        url: 'http://localhost:10832',
        port: 10832,
        tags: ['ai', 'inference']
    },
    {
        id: 'devices-mcp',
        label: 'Devices & IoT',
        description: 'Tapo, Netatmo, and smart home orchestration',
        icon: Home,
        url: 'http://localhost:10716',
        port: 10716,
        tags: ['iot', 'home']
    },
    {
        id: 'plex-plus',
        label: 'Plex Plus',
        description: 'Premium media management and streaming',
        icon: Tv,
        url: 'http://localhost:10760',
        port: 10760,
        tags: ['media', 'entertainment']
    },
    {
        id: 'email-hub',
        label: 'Email Hub',
        description: 'Federated mailbox and comms automation',
        icon: Mail,
        url: 'http://localhost:10812',
        port: 10812,
        tags: ['comms', 'utility']
    },
    {
        id: 'winrar-mcp',
        label: 'Archive Lab',
        description: 'High-performance compression and extraction',
        icon: Archive,
        url: 'http://localhost:10763',
        port: 10763,
        tags: ['utility', 'files']
    },
    {
        id: 'monitoring-hub',
        label: 'Fleet Monitor',
        description: 'Real-time telemetry and resource analytics',
        icon: Activity,
        url: 'http://localhost:10850',
        port: 10850,
        tags: ['core', 'status']
    },
    {
        id: 'web-dev-mcp',
        label: 'Web Dev Lab',
        description: 'FastAPI and Vite workspace orchestration',
        icon: Layout,
        url: 'http://localhost:10852',
        port: 10852,
        tags: ['dev', 'web']
    },
    {
        id: 'unity3d-mcp',
        label: 'Unity3D Visualizer',
        description: 'Spatial computing and virtual orchestration',
        icon: Box,
        url: 'http://localhost:10830',
        port: 10830,
        tags: ['dev', '3d']
    },
    {
        id: 'blender-mcp',
        label: 'Blender Lab',
        description: '3D modeling and rendering pipeline',
        icon: Box,
        url: 'http://localhost:10848',
        port: 10848,
        tags: ['media', '3d']
    },
    {
        id: 'gimp-mcp',
        label: 'GIMP Studio',
        description: 'Image processing and texture creation',
        icon: Edit3,
        url: 'http://localhost:10772',
        port: 10772,
        tags: ['media', 'design']
    },
    {
        id: 'calibre-mcp',
        label: 'Calibre Library',
        description: 'E-book management and document archival',
        icon: BookOpen,
        url: 'http://localhost:10721',
        port: 10721,
        tags: ['media', 'docs']
    },
    {
        id: 'docker-mcp',
        label: 'Docker Control',
        description: 'Container lifecycle and orchestration',
        icon: Layers,
        url: 'http://localhost:10806',
        port: 10806,
        tags: ['dev', 'infra']
    },
    {
        id: 'observability-hub',
        label: 'Observability',
        description: 'Entire.io checkpoints and provenance',
        icon: Bot,
        url: 'http://localhost:10824',
        port: 10824,
        tags: ['core', 'ops']
    },
    {
        id: 'games-hub',
        label: 'Games Hub',
        description: 'High-performance gaming and meta-site index',
        icon: Gamepad2,
        url: 'http://localhost:10726',
        port: 10726,
        tags: ['media', 'games']
    },
    {
        id: 'fastsearch-hub',
        label: 'FastSearch',
        description: 'Ultra-low latency indexing and retrieval',
        icon: Search,
        url: 'http://localhost:10844',
        port: 10844,
        tags: ['utility', 'search']
    }
];
