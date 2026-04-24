from src.agents.oneagent import OneAgentAuditAgent
from src.agents.auto_tags import AutoTagsAuditAgent
from src.agents.manual_tags import ManualTagsAuditAgent
from src.agents.host_groups import HostGroupsAuditAgent
from src.agents.management_zones import ManagementZonesAuditAgent
from src.agents.security_context import SecurityContextAuditAgent
from src.agents.rum import RumAuditAgent
from src.agents.synthetic import SyntheticAuditAgent
from src.agents.anomaly_detection import AnomalyDetectionAuditAgent
from src.agents.notifications import NotificationsAuditAgent
from src.agents.slos import SlosAuditAgent
from src.agents.ownership import OwnershipAuditAgent

ALL_AGENTS = [
    OneAgentAuditAgent,
    AutoTagsAuditAgent,
    ManualTagsAuditAgent,
    HostGroupsAuditAgent,
    ManagementZonesAuditAgent,
    SecurityContextAuditAgent,
    RumAuditAgent,
    SyntheticAuditAgent,
    AnomalyDetectionAuditAgent,
    NotificationsAuditAgent,
    SlosAuditAgent,
    OwnershipAuditAgent,
]
