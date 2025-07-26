# 🚀 Workflow MCP Server

A Model Context Protocol (MCP) server that allows you to control workflow features from Claude Desktop. This server provides tools to selectively enable/disable various workflow functionalities.

## 📋 Features

### **Controllable Workflow Features:**
- **Email Sending** - Amazon SES email functionality
- **Claude Integration** - AI-powered upsell recommendations
- **Slack Posting** - Slack notifications and summaries
- **Zoom Meeting** - Automated meeting creation
- **MongoDB Integration** - Database operations
- **Usage Endpoint** - Usage data API endpoint

## 🛠️ Available Tools

### 1. **Get Workflow Status**
```bash
get_workflow_status
```
Returns the current status of all workflow features.

### 2. **Disable Workflow Feature**
```bash
disable_workflow_feature --feature "email_sending"
```
Disables a specific workflow feature.

**Available features:**
- `email_sending`
- `claude_integration`
- `slack_posting`
- `zoom_meeting`
- `mongodb_integration`
- `usage_endpoint`

### 3. **Enable Workflow Feature**
```bash
enable_workflow_feature --feature "email_sending"
```
Enables a specific workflow feature.

### 4. **Toggle Workflow Feature**
```bash
toggle_workflow_feature --feature "email_sending"
```
Toggles a feature on/off.

### 5. **Reset All Features**
```bash
reset_workflow_features
```
Resets all features to enabled state.

### 6. **Disable All Features**
```bash
disable_all_workflow_features
```
Disables all workflow features.

## 🎯 Usage Examples

### **From Claude Desktop:**

1. **Disable Email Sending:**
   ```
   "Disable email sending functionality"
   ```

2. **Disable Claude Integration:**
   ```
   "Turn off Claude AI integration"
   ```

3. **Check Current Status:**
   ```
   "What's the current status of workflow features?"
   ```

4. **Enable Specific Feature:**
   ```
   "Enable MongoDB integration"
   ```

5. **Toggle Feature:**
   ```
   "Toggle Slack posting on/off"
   ```

6. **Reset Everything:**
   ```
   "Reset all workflow features to enabled"
   ```

## 📁 Configuration

The server uses a JSON configuration file (`workflow_config.json`) to persist settings:

```json
{
  "email_sending": "enabled",
  "claude_integration": "enabled",
  "slack_posting": "enabled",
  "zoom_meeting": "enabled",
  "mongodb_integration": "enabled",
  "usage_endpoint": "enabled"
}
```

## 🔧 How It Works

### **Configuration Flow:**
1. **MCP Server** receives commands from Claude Desktop
2. **Configuration** is updated in `workflow_config.json`
3. **Workflow Activities** check configuration before executing
4. **Features** are enabled/disabled based on configuration

### **Workflow Integration:**
- Each activity checks if its feature is enabled
- If disabled, the activity skips execution and logs the action
- Workflow continues normally without the disabled feature
- No workflow failures due to disabled features

## 🧪 Testing

Run the test script to verify functionality:

```bash
python test_mcp_server.py
```

This will:
1. Show current status
2. Disable email sending
3. Disable Claude integration
4. Toggle Slack posting
5. Show final status
6. Reset all features

## 📊 Feature Behavior When Disabled

### **Email Sending:**
- Logs: "Email sending is disabled - skipping email"
- Returns success to avoid workflow failure
- No actual email sent

### **Claude Integration:**
- Logs: "Claude integration is disabled - using fallback logic"
- Uses rule-based upsell plan instead of AI
- Workflow continues with fallback data

### **Slack Posting:**
- Logs: "Slack posting is disabled - skipping message"
- Returns mock message ID
- No actual Slack message sent

### **Zoom Meeting:**
- Logs: "Zoom meeting creation is disabled - skipping meeting"
- Returns meeting with "[DISABLED]" prefix
- No actual Zoom meeting created

### **MongoDB Integration:**
- Logs: "MongoDB integration is disabled - using default contract data"
- Returns default contract data
- No database queries performed

### **Usage Endpoint:**
- Endpoint remains available but logs disabled status
- Can be used for testing without actual data

## 🚀 Setup for Claude Desktop

1. **Install MCP Server:**
   ```bash
   # The server is already included in this project
   ```

2. **Configure Claude Desktop:**
   - Add the MCP server to your Claude Desktop configuration
   - Point to the `mcp_server.py` file

3. **Start Using:**
   - Ask Claude to control workflow features
   - Monitor the `workflow_config.json` file for changes
   - Test workflows to see disabled features in action

## 🔍 Monitoring

### **Configuration File:**
- Watch `workflow_config.json` for real-time changes
- File is updated immediately when features are toggled

### **Workflow Logs:**
- Check worker logs for disabled feature messages
- Look for "is disabled - skipping" messages

### **Status Commands:**
- Use `get_workflow_status` to check current state
- All tools return current status after changes

## 🎯 Use Cases

### **Development:**
- Disable email sending during testing
- Turn off external API calls
- Use fallback data instead of real integrations

### **Production:**
- Temporarily disable problematic features
- Control feature rollout
- Manage costs by disabling expensive operations

### **Debugging:**
- Isolate issues by disabling specific features
- Test workflows with minimal external dependencies
- Verify fallback behavior

## 🔒 Security

- Configuration file is local to the project
- No external API calls for configuration
- All changes are logged and visible
- No sensitive data in configuration

## 📝 Notes

- **Persistence:** Configuration changes are saved immediately
- **Default State:** All features start as enabled
- **Workflow Safety:** Disabled features don't cause workflow failures
- **Logging:** All disabled actions are logged for transparency
- **Fallbacks:** Disabled features use appropriate fallback behavior

---

**Ready to control your workflows from Claude Desktop! 🎉** 